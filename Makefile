# Variables
REQUIREMENTS_FILE=requirements.txt
ZIP_FILE=lambda_resources.zip
S3_BUCKET=stark-bucket-for-lambda
S3_ZIP_PATH=s3://$(S3_BUCKET)/lambda_resources.zip
TEMPLATE_FILE=src/template.yaml
STACK_NAME=LambdaStack
TEST_REQUIREMENTS_FILE=tests/test_requirements.txt
TEMP_DIR=src/app/temp_dir

install:
	@echo "Installing dependencies..."
	pip install -r $(REQUIREMENTS_FILE)
deploy:
	@echo "Downloading dependencies..."
	mkdir -p $(TEMP_DIR)
	pip install -r $(REQUIREMENTS_FILE) -t $(TEMP_DIR)
	cp src/app/index.py $(TEMP_DIR)
	@echo "Creating ZIP file..."
	cd $(TEMP_DIR) && zip -r ../../../$(ZIP_FILE) .
	rm -rf $(TEMP_DIR)
	@echo "Creating S3 bucket if it does not exist..."
	aws s3 mb s3://$(S3_BUCKET) || true
	@echo "Uploading ZIP file to S3..."
	aws s3 cp $(ZIP_FILE) $(S3_ZIP_PATH)
	rm $(ZIP_FILE)
	@echo "Deploying CloudFormation stack..."
	aws cloudformation deploy --template-file $(TEMPLATE_FILE) --stack-name $(STACK_NAME) --capabilities CAPABILITY_NAMED_IAM
	@echo "Deployment complete."

tear-down:
	@echo "Tearing down stack created with AWS CloudFormation..."
	aws cloudformation delete-stack --stack-name $(STACK_NAME)

force-tear-down:
	@echo "Forcefully tearing down stack created with AWS CloudFormation (for stacks in DELETE_FAILED state)..."
	aws cloudformation delete-stack --stack-name $(STACK_NAME) --deletion-mode FORCE_DELETE_STACK

test:
	@echo "Installing base dependencies..."
	pip install -r $(REQUIREMENTS_FILE)
	@echo "Installing test dependencies..."
	pip install -r $(TEST_REQUIREMENTS_FILE)
	@echo "Running tests..."
	pytest -vvs .
	@echo "Tests complete."
