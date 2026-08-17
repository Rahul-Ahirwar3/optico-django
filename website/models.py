from django.db import models
from cloudinary.models import CloudinaryField


# ==================================================
# CONTACT
# ==================================================

class Contact(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=15)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


# ==================================================
# PRODUCT / BULB
# ==================================================

class Product(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    image = CloudinaryField('image')

    # Current stock
    stock_quantity = models.PositiveIntegerField(default=0)

    # Selling price
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0
    )

    def __str__(self):
        return self.name


# ==================================================
# BULB ISSUE / SALE
# ==================================================

class Issue(models.Model):

    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='issues'
    )

    customer_name = models.CharField(max_length=100)

    quantity = models.PositiveIntegerField()

    issue_date = models.DateField()

    rate = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    total_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0
    )

    paid_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0
    )

    due_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def save(self, *args, **kwargs):

        # Total amount
        self.total_amount = self.quantity * self.rate

        # Due amount
        self.due_amount = self.total_amount - self.paid_amount

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.product.name} - {self.quantity}"


# ==================================================
# PAYMENT HISTORY
# ==================================================

class Payment(models.Model):

    issue = models.ForeignKey(
        Issue,
        on_delete=models.CASCADE,
        related_name='payments'
    )

    payment_date = models.DateField()

    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    payment_method = models.CharField(
        max_length=50,
        choices=[
            ('Cash', 'Cash'),
            ('UPI', 'UPI'),
            ('Bank', 'Bank'),
            ('Other', 'Other'),
        ],
        default='Cash'
    )

    note = models.TextField(
        blank=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return f"{self.issue.customer_name} - ₹{self.amount}"