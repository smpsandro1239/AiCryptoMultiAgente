provider "aws" {
  region = "eu-west-1"
}

resource "aws_instance" "matf_server" {
  ami           = "ami-0c55b159cbfafe1f0" # Exemplo Ubuntu
  instance_type = "t3.medium"

  tags = {
    Name = "MATF-Trading-Node"
  }
}

resource "aws_db_instance" "matf_db" {
  allocated_storage    = 20
  engine               = "postgres"
  instance_class       = "db.t3.micro"
  db_name              = "matf_persistent"
  username             = "admin"
  password             = "matf_secure_pass"
  skip_final_snapshot  = true
}
