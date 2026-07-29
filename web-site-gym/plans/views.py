from rest_framework.views import APIView, Response, status
from django.core.exceptions import ObjectDoesNotExist
from .services import create_preference, create_plan, cancel_plan, user_plan_is_active, update_plan, get_payment_mercadopago
from django.db.utils import IntegrityError
from .models import Plan


# Create your views here.


#  Rota: /gym/plan-payment/
class PlanView(APIView):

    def post(self, request) -> Response:
        user = request.user
        data = request.data

        if user_plan_is_active(user):
            return Response({'error': '❌ Plano já está ativo.'}, status=status.HTTP_400_BAD_REQUEST)

        else:
            print('objects dont exists')
            data = create_preference(data["plan"], user)

            return Response(data, status=status.HTTP_200_OK)


#  Rota: /gym/payments/confirm/
class PaymentConfirmView(APIView):
    def post(self, request) -> Response:
        payment_id = request.data.get('payment_id')
        if not payment_id:
            return Response({'error': 'PaymentId no provide'}, status=status.HTTP_400_BAD_REQUEST)
        payment = get_payment_mercadopago(int(payment_id))

        user = request.user
        payment_user_id = payment['additional_info']['items'][0]['id']
        if payment_user_id != str(user.id):
            return Response(
                {'error': 'The payment ID is not the same as the user ID'},
                status=status.HTTP_400_BAD_REQUEST
            )

        if payment['status'] != 'approved':
            return Response({'error': 'Invalid payment'}, status=status.HTTP_400_BAD_REQUEST)

        plan_kind = payment['additional_info']['items'][0]['category_id']

        try:
            plan = Plan.objects.get(payment_id=payment_id)
            return Response({
                'plan_name': plan.kind_plan,
                'expires_at': plan.expected_payment,
                'is_active': plan.is_valid
            }, status=status.HTTP_200_OK)

        except ObjectDoesNotExist:
            try:
                if Plan.objects.filter(user=user).exists():
                    plan = update_plan(user, plan_kind, payment_id)

                    return Response({
                        'plan_name': plan.kind_plan,
                        'expires_at': plan.expected_payment,
                        'is_active': plan.is_valid
                    }, status=status.HTTP_200_OK)

                plan = create_plan(user, plan_kind, payment_id)

                return Response({
                    'plan_name': plan.kind_plan,
                    'expires_at': plan.expected_payment,
                    'is_active': plan.is_valid
                }, status=status.HTTP_200_OK)

            except Exception:
                return Response({}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


#  Route: /gym/payments/status/
class PlanStatusView(APIView):

    def get(self, request) -> Response:
        user = request.user
        try:
            user_plan = user.plan
            print('is_active:', user_plan.is_active, 'is_valid:', user_plan.is_valid)
            if not user_plan.is_valid:
                raise ObjectDoesNotExist
            return Response({
                'plan_name': user_plan.kind_plan,
                'expires_at': user_plan.expected_payment,
                'is_active': user_plan.is_active
            }, status=status.HTTP_200_OK)

        except ObjectDoesNotExist:
            return Response({}, status=status.HTTP_400_BAD_REQUEST)


#  Route: /gym/plan/cancel/
class PlanCancelView(APIView):
    def post(self, request) -> Response:
        user = request.user
        try:
            plan = cancel_plan(user)

            if plan is None:
                return Response({
                    'error': 'Internal server error'
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

            return Response({
                'plan_name': plan.kind_plan,
                'expires_at': plan.expected_payment,
                'is_active': plan.is_valid
            }, status=status.HTTP_200_OK)

        except Exception as e:
            print(e.args)
            return Response({}, status=status.HTTP_400_BAD_REQUEST)
