from django.shortcuts import render
from django.db.models import Value, F, Func, ExpressionWrapper, DecimalField
from django.db.models.aggregates import Count, Max, Min, Avg
from store.models import Customer, Collection, Product, Order, OrderItem
from tags.models import TaggedItem
from django.core.mail import EmailMessage, send_mail, mail_admins, BadHeaderError
from templated_mail.mail import BaseEmailMessage


def index(request):
    # queryset = (
    #     Order.objects.select_related("collection")
    #     .filter(id__in=OrderItem.objects.values("product_id").distinct())
    #     .order_by("title")
    # )
    # queryset = (
    #     Order.objects.select_related("customer")
    #     .prefetch_related("orderitem_set__product")
    #     .order_by("-placed_at")[:20]
    # )
    # ag = Order.objects.aggregate(count=Count(id))
    # ag = OrderItem.objects.filter(product__id=1).aggregate(count=Count(id))
    # ag = Order.objects.filter(customer__id=1).aggregate(count=Count(id))
    # ag = Product.objects.filter(collection__id=3).aggregate(
    #     min=Min("unit_price"), max=Max("unit_price"), avg=Avg("unit_price")
    # )
    # queryset = Customer.objects.annotate(
    #     full_name=Func(F("first_name"), Value(" "), F("last_name"), function="CONCAT")
    # )
    # queryset = Customer.objects.annotate(orders_count=Count("order"))
    # discount_price = ExpressionWrapper(
    #     F("unit_price") * 0.8, output_field=DecimalField()
    # )
    # queryset = Product.objects.annotate(discount_price=discount_price)
    # TaggedItem.object.get_tags_for(Product, 1)
    try:
        message = BaseEmailMessage(
            template_name='emails/hello.html',
            context={
                'name': 'Omar'
            }
        )
        message.send(['omar@example.com'])
        # message = EmailMessage(
        #     "subject", "message", "info@omar.com", ["omarswailam@outlook.com"]
        # )
        # message.attach_file("")
        # message.send()
        # mail_admins("subject", "message", html_message="message")
        # send_mail("subject", "message", "info@omar.com", ["omarswailam@outlook.com"])
    except BadHeaderError:
        print("bad header error")
    return render(request, "index.html", {"name": "omar"})
