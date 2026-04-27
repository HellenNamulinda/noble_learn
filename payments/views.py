from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView

from courses.models import Course
from progress.models import Enrollment
from .models import Order
from .serializers import OrderSerializer


class CreateCheckoutSessionView(APIView):
    """
    Creates and fulfills an order without an external payment gateway.
    """

    def post(self, request):
        course_id = request.data.get('course_id')
        order_type = request.data.get('order_type', Order.COURSE_UNLOCK)

        if order_type not in (Order.COURSE_UNLOCK, Order.CERTIFICATE):
            return Response(
                {'detail': 'order_type must be "course" or "certificate".'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            course = Course.objects.get(pk=course_id, is_published=True)
        except Course.DoesNotExist:
            return Response({'detail': 'Course not found.'}, status=status.HTTP_404_NOT_FOUND)

        if order_type == Order.COURSE_UNLOCK:
            if Enrollment.objects.filter(user=request.user, course=course, is_paid=True).exists():
                return Response({'detail': 'Already purchased.'}, status=status.HTTP_400_BAD_REQUEST)
            amount = course.price
            detail = f'Course unlocked: {course.title}'
        else:
            enrollment = Enrollment.objects.filter(
                user=request.user, course=course, is_paid=True
            ).first()
            if not enrollment:
                return Response(
                    {'detail': 'Complete the course first.'},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            amount = course.certificate_price
            detail = f'Certificate purchased: {course.title}'

        order = Order.objects.create(
            user=request.user,
            course=course,
            order_type=order_type,
            amount=amount,
            status=Order.COMPLETED,
        )

        if order.order_type == Order.COURSE_UNLOCK:
            Enrollment.objects.update_or_create(
                user=order.user,
                course=order.course,
                defaults={'is_paid': True},
            )
        else:
            from certificates.utils import generate_certificate
            generate_certificate(order.user, order.course, order)

        return Response(
            {
                'order_id': str(order.id),
                'status': order.status,
                'detail': detail,
            },
            status=status.HTTP_201_CREATED,
        )


class OrderListView(generics.ListAPIView):
    serializer_class = OrderSerializer

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user)
