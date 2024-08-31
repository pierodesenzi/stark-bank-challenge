import starkbank
import os
import random
import time
from datetime import datetime, timedelta
from faker import Faker

# Initialize Faker for generating random names
faker = Faker()

# Setting up credentials for Stark Bank's API
private_key = os.getenv("PRIVATE_KEY")
project = starkbank.Project(
    environment="sandbox",
    id=os.getenv("PROJECT_ID"),
    private_key=private_key,
)
starkbank.user = project


# Loop for 24 hours, issuing invoices every 3 hours
end_time = datetime.utcnow() + timedelta(hours=24)

while datetime.utcnow() < end_time:
    # Generate a random number of invoices between 8 and 12
    num_invoices = random.randint(8, 12)

    for _ in range(0, num_invoices):
        _ = starkbank.invoice.create(
            [
                starkbank.Invoice(
                    amount=random.randint(1, 100),
                    name=faker.name(),
                    tax_id="13793881040",
                    due=datetime.utcnow() + timedelta(hours=1),
                    expiration=timedelta(hours=3).total_seconds(),
                    fine=5,  # 5% fine
                    interest=2.5,  # 2.5% per month interest
                    tags=["immediate"],
                )
            ]
        )

    # Wait for 3 hours before issuing the next batch of invoices
    time.sleep(3 * 60 * 60)
