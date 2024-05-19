from django.db import models
from django.core.exceptions import ValidationError
from authentication.models import CustomUser as User
from django.core.validators import MinValueValidator, MaxValueValidator


class Market(models.Model):
    name = models.CharField(max_length=1000)
    description = models.TextField(default='')
    @classmethod
    def get_all(cls):
        return cls.objects.all()
    
    def __str__(self) -> str:
        return self.name


class Cart(models.Model):
    user = models.ForeignKey(User, related_name='cart', on_delete=models.CASCADE)
    market = models.ForeignKey(Market, related_name='products', on_delete=models.PROTECT)
    title = models.CharField(max_length=1000)
    image = models.URLField()
    rating = models.FloatField(null=True)
    price = models.FloatField(default=0.0)
    status_accepted = models.BooleanField(db_default=False, null=False, blank=True) # I use here bool field to make database holding small value 
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def status(self):
        if not self.status_accepted:
            return 'Pending'
        else:
            return 'Accepted'

    def __str__(self):
        return f"{self.market.name} product  |  {self.status}"
    
    def accept_product(self):
        if not self.status_accepted :
            try:
                self.status_accepted = True
                self.save()
            except Exception as e:
                print(e)
                return False
        else:
            raise ValidationError("Product already accepted")

    @classmethod
    def get_pending(cls, user):
        return cls.objects.filter(user=user, status_accepted = False)

    @classmethod
    def get_accepted(cls, user):
        return cls.objects.filter(user=user, status_accepted = True)


class Order(models.Model):
    cart = models.ManyToManyField(Cart, related_name='orders')
    token = models.CharField(max_length=100, unique=True)
    is_paid = models.BooleanField(default=False)
    is_arrived = models.BooleanField(default=False)
    rate = models.PositiveSmallIntegerField(
        null=True,
        blank=True,
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


    def __str__(self):
        return f"Order-{self.pk}"
    
    def paid(self):
        if self.is_paid:
            raise ValidationError("Order is alredy paid")
        self.is_paid = True
        self.save()    

    def arrived(self):
        if self.is_arrived:
            raise ValidationError("Order is alredy arrived")
        self.is_arrived = True
        self.save()    
