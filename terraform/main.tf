/* BUDDY AI OS - TERRAFORM INFRASTRUCTURE AS CODE
   Complete global infrastructure automation for 3 regions
   Execution: terraform plan && terraform apply
*/

terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
  backend "s3" {
    bucket = "buddy-terraform-state"
    key    = "prod/terraform.tfstate"
    region = "us-east-1"
  }
}

provider "aws" {
  region = var.primary_region
}

# ============================================================================
# VARIABLES
# ============================================================================

variable "primary_region" {
  default = "us-east-1"
}

variable "secondary_regions" {
  default = ["eu-west-1", "ap-southeast-1"]
}

variable "cluster_name" {
  default = "buddy-ai"
}

variable "api_docker_image" {
  default = "buddy-ai/api:latest"
}

variable "agent_docker_image" {
  default = "buddy-ai/agents:latest"
}

# ============================================================================
# VPC AND NETWORKING
# ============================================================================

resource "aws_vpc" "buddy" {
  for_each            = toset([var.primary_region] + var.secondary_regions)
  provider            = aws
  cidr_block          = each.key == var.primary_region ? "10.0.0.0/16" : (each.key == "eu-west-1" ? "10.1.0.0/16" : "10.2.0.0/16")
  enable_dns_hostnames = true
  enable_dns_support  = true

  tags = {
    Name   = "buddy-vpc-${each.key}"
    Region = each.key
  }
}

resource "aws_subnet" "buddy_public" {
  for_each          = toset([var.primary_region] + var.secondary_regions)
  provider          = aws
  vpc_id            = aws_vpc.buddy[each.key].id
  cidr_block        = each.key == var.primary_region ? "10.0.1.0/24" : (each.key == "eu-west-1" ? "10.1.1.0/24" : "10.2.1.0/24")
  availability_zone = "${each.key}a"

  tags = {
    Name = "buddy-subnet-public-${each.key}"
  }
}

resource "aws_internet_gateway" "buddy" {
  for_each = toset([var.primary_region] + var.secondary_regions)
  provider = aws
  vpc_id   = aws_vpc.buddy[each.key].id

  tags = {
    Name = "buddy-igw-${each.key}"
  }
}

# ============================================================================
# SECURITY GROUPS
# ============================================================================

resource "aws_security_group" "buddy_alb" {
  for_each    = toset([var.primary_region] + var.secondary_regions)
  provider    = aws
  name        = "buddy-alb-sg-${each.key}"
  vpc_id      = aws_vpc.buddy[each.key].id
  description = "Security group for ALB"

  ingress {
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name = "buddy-alb-sg-${each.key}"
  }
}

# ============================================================================
# RDS POSTGRESQL
# ============================================================================

resource "aws_db_subnet_group" "buddy" {
  for_each            = toset([var.primary_region] + var.secondary_regions)
  provider            = aws
  name                = "buddy-db-subnet-${each.key}"
  subnet_ids          = [aws_subnet.buddy_public[each.key].id]
  skip_final_snapshot = true

  tags = {
    Name = "buddy-db-subnet-${each.key}"
  }
}

resource "aws_rds_cluster" "buddy_primary" {
  provider                  = aws
  cluster_identifier        = "buddy-primary"
  engine                    = "aurora-postgresql"
  engine_version            = "15.3"
  database_name             = "buddy_db"
  master_username           = "admin"
  master_password           = random_password.db_password.result
  db_subnet_group_name      = aws_db_subnet_group.buddy[var.primary_region].name
  vpc_security_group_ids    = [aws_security_group.buddy_alb[var.primary_region].id]
  backup_retention_period   = 30
  preferred_backup_window   = "03:00-04:00"
  copy_tags_to_snapshot     = true
  storage_encrypted         = true
  kms_key_id                = aws_kms_key.buddy.arn
  enable_cloudwatch_logs_exports = ["postgresql"]
  skip_final_snapshot       = false
  final_snapshot_identifier = "buddy-final-snapshot-${formatdate("YYYY-MM-DD-hhmm", timestamp())}"

  tags = {
    Name = "buddy-primary-cluster"
  }
}

resource "aws_rds_cluster_instance" "buddy_primary" {
  provider           = aws
  cluster_identifier = aws_rds_cluster.buddy_primary.id
  instance_class     = "db.r6i.large"
  engine              = aws_rds_cluster.buddy_primary.engine
  engine_version      = aws_rds_cluster.buddy_primary.engine_version
  publicly_accessible = false

  tags = {
    Name = "buddy-primary-instance"
  }
}

resource "random_password" "db_password" {
  length  = 32
  special = true
}

# ============================================================================
# KMS ENCRYPTION KEY
# ============================================================================

resource "aws_kms_key" "buddy" {
  description             = "KMS key for Buddy AI OS encryption"
  deletion_window_in_days = 7
  enable_key_rotation     = true

  tags = {
    Name = "buddy-kms-key"
  }
}

resource "aws_kms_alias" "buddy" {
  name          = "alias/buddy-encryption"
  target_key_id = aws_kms_key.buddy.key_id
}

# ============================================================================
# S3 BUCKETS FOR BACKUPS
# ============================================================================

resource "aws_s3_bucket" "buddy_backups" {
  for_each = toset([var.primary_region] + var.secondary_regions)
  provider = aws
  bucket   = "buddy-backups-${each.key}-${data.aws_caller_identity.current.account_id}"

  tags = {
    Name = "buddy-backups-${each.key}"
  }
}

resource "aws_s3_bucket_versioning" "buddy_backups" {
  for_each = aws_s3_bucket.buddy_backups
  provider = aws
  bucket   = each.value.id

  versioning_configuration {
    status = "Enabled"
  }
}

resource "aws_s3_bucket_server_side_encryption_configuration" "buddy_backups" {
  for_each = aws_s3_bucket.buddy_backups
  provider = aws
  bucket   = each.value.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm     = "aws:kms"
      kms_master_key_id = aws_kms_key.buddy.arn
    }
  }
}

# ============================================================================
# EKS CLUSTERS
# ============================================================================

resource "aws_eks_cluster" "buddy" {
  for_each            = toset([var.primary_region] + var.secondary_regions)
  provider            = aws
  name                = "buddy-${each.key}"
  version             = "1.28"
  role_arn            = aws_iam_role.eks_cluster.arn
  vpc_config {
    subnet_ids = [aws_subnet.buddy_public[each.key].id]
  }

  depends_on = [aws_iam_role_policy_attachment.eks_cluster_policy]

  tags = {
    Name   = "buddy-eks-${each.key}"
    Region = each.key
  }
}

resource "aws_eks_node_group" "buddy" {
  for_each            = toset([var.primary_region] + var.secondary_regions)
  provider            = aws
  cluster_name        = aws_eks_cluster.buddy[each.key].name
  node_group_name     = "buddy-nodes-${each.key}"
  node_role_arn       = aws_iam_role.eks_node.arn
  subnet_ids          = [aws_subnet.buddy_public[each.key].id]
  scaling_config {
    min_size     = each.key == var.primary_region ? 10 : 5
    max_size     = each.key == var.primary_region ? 100 : 50
    desired_size = each.key == var.primary_region ? 10 : 5
  }
  instance_types = [each.key == var.primary_region ? "t3.xlarge" : "t3.large"]

  tags = {
    Name = "buddy-nodegroup-${each.key}"
  }
}

# ============================================================================
# IAM ROLES
# ============================================================================

resource "aws_iam_role" "eks_cluster" {
  name = "buddy-eks-cluster-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Action = "sts:AssumeRole"
      Effect = "Allow"
      Principal = {
        Service = "eks.amazonaws.com"
      }
    }]
  })
}

resource "aws_iam_role_policy_attachment" "eks_cluster_policy" {
  policy_arn = "arn:aws:iam::aws:policy/AmazonEKSClusterPolicy"
  role       = aws_iam_role.eks_cluster.name
}

resource "aws_iam_role" "eks_node" {
  name = "buddy-eks-node-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Action = "sts:AssumeRole"
      Effect = "Allow"
      Principal = {
        Service = "ec2.amazonaws.com"
      }
    }]
  })
}

resource "aws_iam_role_policy_attachment" "eks_node_policy" {
  policy_arn = "arn:aws:iam::aws:policy/AmazonEKSWorkerNodePolicy"
  role       = aws_iam_role.eks_node.name
}

# ============================================================================
# ELASTICACHE REDIS
# ============================================================================

resource "aws_elasticache_subnet_group" "buddy" {
  for_each    = toset([var.primary_region] + var.secondary_regions)
  provider    = aws
  name        = "buddy-redis-subnet-${each.key}"
  subnet_ids  = [aws_subnet.buddy_public[each.key].id]
  description = "Redis subnet group for ${each.key}"
}

resource "aws_elasticache_cluster" "buddy" {
  for_each               = toset([var.primary_region] + var.secondary_regions)
  provider              = aws
  cluster_id            = "buddy-redis-${each.key}"
  engine                = "redis"
  node_type             = each.key == var.primary_region ? "cache.r6g.large" : "cache.r6g.xlarge"
  num_cache_nodes       = each.key == var.primary_region ? 6 : 3
  port                  = 6379
  parameter_group_name  = "default.redis7"
  subnet_group_name     = aws_elasticache_subnet_group.buddy[each.key].name
  at_rest_encryption_enabled = true
  transit_encryption_enabled = true
  kms_key_id            = aws_kms_key.buddy.id
  automatic_failover_enabled = true
  engine_version        = "7.0"
  snapshot_retention_limit = 30

  tags = {
    Name = "buddy-redis-${each.key}"
  }
}

# ============================================================================
# ROUTE53 DNS
# ============================================================================

resource "aws_route53_zone" "buddy" {
  name = "buddy-ai.global"

  tags = {
    Name = "buddy-ai-zone"
  }
}

resource "aws_route53_record" "api" {
  for_each = toset([var.primary_region] + var.secondary_regions)
  zone_id  = aws_route53_zone.buddy.zone_id
  name     = "api.buddy-ai.global"
  type     = "A"
  set_identifier = each.key

  latency_routing_policy {
    region = each.key
  }

  alias {
    name                   = "buddy-alb-${each.key}.amazonaws.com"
    zone_id                = "Z35SXDOTRQ7X7K" # ALB zone ID
    evaluate_target_health = true
  }
}

# ============================================================================
# CLOUDFRONT CDN
# ============================================================================

resource "aws_cloudfront_distribution" "buddy" {
  provider = aws
  enabled  = true

  origin {
    domain_name = "api.buddy-ai.global"
    origin_id   = "buddy-api"

    custom_origin_config {
      http_port              = 80
      https_port             = 443
      origin_protocol_policy = "https-only"
      origin_ssl_protocols   = ["TLSv1.2"]
    }
  }

  default_cache_behavior {
    allowed_methods  = ["GET", "HEAD", "OPTIONS"]
    cached_methods   = ["GET", "HEAD"]
    target_origin_id = "buddy-api"
    compress         = true

    forwarded_values {
      query_string = true
      cookies {
        forward = "all"
      }
    }

    viewer_protocol_policy = "redirect-to-https"
    default_ttl            = 300
    max_ttl                = 3600
  }

  viewer_certificate {
    cloudfront_default_certificate = true
  }

  restrictions {
    geo_restriction {
      restriction_type = "none"
    }
  }

  tags = {
    Name = "buddy-cdn"
  }
}

# ============================================================================
# OUTPUTS
# ============================================================================

data "aws_caller_identity" "current" {}

output "eks_cluster_names" {
  value = {
    for region, cluster in aws_eks_cluster.buddy : region => cluster.name
  }
}

output "rds_endpoint" {
  value       = aws_rds_cluster.buddy_primary.endpoint
  description = "RDS cluster endpoint"
}

output "redis_endpoints" {
  value = {
    for region, cluster in aws_elasticache_cluster.buddy : region => cluster.cache_nodes[0].address
  }
  description = "Redis endpoints by region"
}

output "route53_zone_id" {
  value       = aws_route53_zone.buddy.zone_id
  description = "Route53 hosted zone ID"
}

output "cloudfront_domain" {
  value       = aws_cloudfront_distribution.buddy.domain_name
  description = "CloudFront distribution domain"
}

output "db_password" {
  value       = random_password.db_password.result
  sensitive   = true
  description = "Database password (store in secrets manager)"
}
