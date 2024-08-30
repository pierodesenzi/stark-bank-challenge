# Makefile

# Variables
REQUIREMENTS_FILE=src/function/requirements.txt
ZIP_FILE=lambda_resources.zip
S3_BUCKET=stark-service
S3_ZIP_PATH=s3://$(S3_BUCKET)/lambda_resources.zip
TEMPLATE_FILE=src/template.yaml
STACK_NAME=LambdaStack9
TEST_REQUIREMENTS_FILE=tests/requirements.txt
TEMP_DIR=src/function/temp_dir

# Deploy Routine
deploy:
	@echo "Installing dependencies..."
	mkdir -p $(TEMP_DIR)
	pip install -r $(REQUIREMENTS_FILE) -t $(TEMP_DIR)
	mkdir src/function/temp_dir
	pip install -r $(REQUIREMENTS_FILE) -t src/function/
	cp src/function/index.py $(TEMP_DIR)
	@echo "Creating ZIP file..."
	zip -r $(ZIP_FILE) $(TEMP_DIR)
	rm -rf $(TEMP_DIR)
	@echo "Creating S3 bucket..."
	aws s3 mb s3://$(S3_BUCKET) || true # Use 'true' to ignore errors if bucket already exists
	@echo "Uploading ZIP file to S3..."
	aws s3 cp $(ZIP_FILE) $(S3_ZIP_PATH)
	@echo "Deploying CloudFormation stack..."
	aws cloudformation deploy --template-file $(TEMPLATE_FILE) --stack-name $(STACK_NAME) --capabilities CAPABILITY_NAMED_IAM
	@echo "Deployment complete."

tear-down:
	aws cloudformation delete-stack --stack-name $(STACK_NAME)

# Test Routine
test:
	@echo "Installing test dependencies..."
	pip install -r $(TEST_REQUIREMENTS_FILE)
	@echo "Running tests..."
	pytest -vvs .
	@echo "Tests complete."

part:
	mkdir -p $(TEMP_DIR)
	pip install -r $(REQUIREMENTS_FILE) -t $(TEMP_DIR)

# Default target
all: deploy test
