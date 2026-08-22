from django.db import models
from django.db.models import Sum
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from cloudinary.models import CloudinaryField


# ==================================================
# CONTACT
# ==================================================

class Contact(models.Model):

    name = models.CharField(
        max_length=100
    )

    email = models.EmailField()

    phone = models.CharField(
        max_length=15
    )

    message = models.TextField()

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return self.name


# ==================================================
# CUSTOMER / DISTRIBUTOR
# ==================================================

class Customer(models.Model):

    name = models.CharField(
        max_length=100,
        unique=True
    )

    phone = models.CharField(
        max_length=15,
        blank=True
    )

    address = models.TextField(
        blank=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return self.name


# ==================================================
# PRODUCT
# ==================================================

class Product(models.Model):

    name = models.CharField(
        max_length=100
    )

    watt = models.PositiveIntegerField(
        default=0
    )

    description = models.TextField(
        blank=True
    )

    image = CloudinaryField(
        'image',
        blank=True,
        null=True
    )

    total_manufactured = models.PositiveIntegerField(
        default=0
    )

    available_stock = models.PositiveIntegerField(
        default=0
    )

    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0
    )

    class Meta:
        ordering = ['watt']

    def __str__(self):
        return self.name


# ==================================================
# MANUFACTURING
# ==================================================

class Manufacturing(models.Model):

    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='manufacturing'
    )

    date = models.DateField()

    workers = models.PositiveIntegerField(
        default=1
    )

    quantity_manufactured = models.PositiveIntegerField()

    total_stock = models.PositiveIntegerField(
        default=0
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def save(self, *args, **kwargs):

        super().save(*args, **kwargs)

        # ------------------------------------------
        # RUNNING STOCK
        # ------------------------------------------

        records = (
            Manufacturing.objects
            .filter(product=self.product)
            .order_by('date', 'id')
        )

        running_total = 0

        for record in records:

            running_total += (
                record.quantity_manufactured
            )

            if record.total_stock != running_total:

                Manufacturing.objects.filter(
                    id=record.id
                ).update(
                    total_stock=running_total
                )

        # ------------------------------------------
        # TOTAL MANUFACTURED
        # ------------------------------------------

        total_manufactured = (
            Manufacturing.objects
            .filter(product=self.product)
            .aggregate(
                total=Sum(
                    'quantity_manufactured'
                )
            )['total'] or 0
        )

        # ------------------------------------------
        # TOTAL ISSUED
        # ------------------------------------------

        total_issued = (
            Issue.objects
            .filter(product=self.product)
            .aggregate(
                total=Sum('quantity')
            )['total'] or 0
        )

        # ------------------------------------------
        # UPDATE PRODUCT STOCK
        # ------------------------------------------

        self.product.total_manufactured = (
            total_manufactured
        )

        self.product.available_stock = max(
            total_manufactured - total_issued,
            0
        )

        self.product.save(
            update_fields=[
                'total_manufactured',
                'available_stock'
            ]
        )

    def __str__(self):

        return (
            f"{self.product.name} - "
            f"{self.date} - "
            f"{self.quantity_manufactured}"
        )


# ==================================================
# ISSUE / SALE
# ==================================================

class Issue(models.Model):

    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='issues'
    )

    customer = models.ForeignKey(
        Customer,
        on_delete=models.PROTECT,
        related_name='issues'
    )

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

        # ------------------------------------------
        # TOTAL AMOUNT
        # ------------------------------------------

        self.total_amount = (
            self.quantity * self.rate
        )

        # ------------------------------------------
        # DUE AMOUNT
        # ------------------------------------------

        self.due_amount = (
            self.total_amount -
            self.paid_amount
        )

        if self.due_amount < 0:
            self.due_amount = 0

        super().save(*args, **kwargs)

        # ------------------------------------------
        # UPDATE PRODUCT STOCK
        # ------------------------------------------

        total_manufactured = (
            Manufacturing.objects
            .filter(product=self.product)
            .aggregate(
                total=Sum(
                    'quantity_manufactured'
                )
            )['total'] or 0
        )

        total_issued = (
            Issue.objects
            .filter(product=self.product)
            .aggregate(
                total=Sum('quantity')
            )['total'] or 0
        )

        self.product.total_manufactured = (
            total_manufactured
        )

        self.product.available_stock = max(
            total_manufactured - total_issued,
            0
        )

        self.product.save(
            update_fields=[
                'total_manufactured',
                'available_stock'
            ]
        )

    def __str__(self):

        return (
            f"{self.product.name} - "
            f"{self.customer.name} - "
            f"{self.quantity}"
        )


# ==================================================
# PAYMENT
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

        return (
            f"{self.issue.customer.name} - "
            f"₹{self.amount}"
        )


# ==================================================
# ACCOUNT
# ==================================================

class Account(models.Model):

    # ------------------------------------------
    # ONE CUSTOMER = ONE ACCOUNT
    # ------------------------------------------

    customer = models.OneToOneField(
        Customer,
        on_delete=models.CASCADE,
        related_name='account'
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    class Meta:

        ordering = [
            'customer__name'
        ]

        verbose_name = 'Account'

        verbose_name_plural = 'Accounts'

    # ------------------------------------------
    # TOTAL AMOUNT
    # ------------------------------------------

    @property
    def total_amount(self):

        return (
            Issue.objects
            .filter(
                customer=self.customer
            )
            .aggregate(
                total=Sum('total_amount')
            )['total'] or 0
        )

    # ------------------------------------------
    # PAID AMOUNT
    # ------------------------------------------

    @property
    def paid_amount(self):

        payment_total = (
            Payment.objects
            .filter(
                issue__customer=self.customer
            )
            .aggregate(
                total=Sum('amount')
            )['total']
        )

        # Actual Payment entries available
        if payment_total is not None:
            return payment_total

        # Otherwise Issue paid amount
        return (
            Issue.objects
            .filter(
                customer=self.customer
            )
            .aggregate(
                total=Sum('paid_amount')
            )['total'] or 0
        )

    # ------------------------------------------
    # DUE AMOUNT
    # ------------------------------------------

    @property
    def due_amount(self):

        due = (
            self.total_amount -
            self.paid_amount
        )

        return max(
            due,
            0
        )

    def __str__(self):

        return (
            f"{self.customer.name} Account"
        )


# ==================================================
# NET QUANTITY
# ==================================================

class NetQuantity(models.Model):

    product = models.OneToOneField(
        Product,
        on_delete=models.CASCADE,
        related_name='net_quantity'
    )

    total_manufactured = models.PositiveIntegerField(
        default=0
    )

    total_issued = models.PositiveIntegerField(
        default=0
    )

    net_quantity = models.PositiveIntegerField(
        default=0
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    def update_quantity(self):

        self.total_manufactured = (
            Manufacturing.objects
            .filter(product=self.product)
            .aggregate(
                total=Sum(
                    'quantity_manufactured'
                )
            )['total'] or 0
        )

        self.total_issued = (
            Issue.objects
            .filter(product=self.product)
            .aggregate(
                total=Sum('quantity')
            )['total'] or 0
        )

        self.net_quantity = max(
            self.total_manufactured -
            self.total_issued,
            0
        )

        self.save()

    def __str__(self):

        return (
            f"{self.product.name} - "
            f"Net Quantity: "
            f"{self.net_quantity}"
        )


# ==================================================
# INVENTORY
# ==================================================

class Inventory(models.Model):

    class Meta:

        verbose_name = 'Inventory'

        verbose_name_plural = 'Inventory'

    def __str__(self):

        return 'Inventory'


# ==================================================
# NET QUANTITY UPDATE FUNCTION
# ==================================================

def update_net_quantity(product):

    net_quantity, created = (
        NetQuantity.objects
        .get_or_create(
            product=product
        )
    )

    total_manufactured = (
        Manufacturing.objects
        .filter(product=product)
        .aggregate(
            total=Sum(
                'quantity_manufactured'
            )
        )['total'] or 0
    )

    total_issued = (
        Issue.objects
        .filter(product=product)
        .aggregate(
            total=Sum('quantity')
        )['total'] or 0
    )

    net = max(
        total_manufactured -
        total_issued,
        0
    )

    net_quantity.total_manufactured = (
        total_manufactured
    )

    net_quantity.total_issued = (
        total_issued
    )

    net_quantity.net_quantity = (
        net
    )

    net_quantity.save()


# ==================================================
# MANUFACTURING SIGNALS
# ==================================================

@receiver(
    post_save,
    sender=Manufacturing
)
def manufacturing_saved(
    sender,
    instance,
    **kwargs
):

    update_net_quantity(
        instance.product
    )


@receiver(
    post_delete,
    sender=Manufacturing
)
def manufacturing_deleted(
    sender,
    instance,
    **kwargs
):

    update_net_quantity(
        instance.product
    )


# ==================================================
# ISSUE SIGNALS
# ==================================================

@receiver(
    post_save,
    sender=Issue
)
def issue_saved(
    sender,
    instance,
    **kwargs
):

    update_net_quantity(
        instance.product
    )


@receiver(
    post_delete,
    sender=Issue
)
def issue_deleted(
    sender,
    instance,
    **kwargs
):

    update_net_quantity(
        instance.product
    )


# ==================================================
# AUTOMATIC ACCOUNT CREATION
# ==================================================

@receiver(
    post_save,
    sender=Customer
)
def customer_account_created(
    sender,
    instance,
    **kwargs
):

    Account.objects.get_or_create(
        customer=instance
    )
# ==================================================
# AUTO CREATE ACCOUNT FOR CUSTOMER
# ==================================================

# ==================================================
# AUTOMATIC ACCOUNT CREATION
# ==================================================

@receiver(
    post_save,
    sender=Customer
)
def customer_account_created(
    sender,
    instance,
    created,
    **kwargs
):

    if created:
        Account.objects.get_or_create(
            customer=instance
        )