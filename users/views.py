from api.permissions import AdminPermission
from api_yamdb import settings
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from rest_framework import filters, status, viewsets
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import AccessToken

from .models import User
from .serializers import CodeSerializer, EmailSerializer, UserSerializer

generator = default_token_generator


class AdminProfileViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    lookup_field = 'username'
    filter_backends = [filters.SearchFilter]
    search_fields = ('email', )
    permission_classes = (AdminPermission, )

    @action(
        detail=False,
        methods=['GET', 'PATCH'], permission_classes=[IsAuthenticated]
    )
    def me(self, request):
        serializer = UserSerializer(
            request.user,
            data=request.data,
            partial=True)
        if request.method == 'GET':
            serializer = UserSerializer(request.user)
            return Response(serializer.data)
        elif request.method == 'PATCH':
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data)


@api_view(['POST'])
@permission_classes([AllowAny])
def confirmation_code_sender(request):
    serializer = EmailSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    email = serializer.data['email']
    user = User.objects.get_or_create(email=email)[0]
    confirmation_code = generator.make_token(user)
    send_mail(
        subject='Ваш персональный код',
        from_email=settings.DEFAULT_FROM_EMAIL,
        message=f'Ваш код: {confirmation_code}.',
        recipient_list=[email],
        fail_silently=False,
    )
    return Response(
        {"message": f"Код отправлен на почту: {email}"},
        status=status.HTTP_200_OK
    )


@api_view(['POST'])
@permission_classes([AllowAny])
def get_token(request):
    serializer = CodeSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    email = serializer.data['email']
    username = serializer.data['username']
    confirmation_code = serializer.data['confirmation_code']
    user = get_object_or_404(User, email=email, username=username)
    check_token = default_token_generator.check_token(user, confirmation_code)
    if check_token is False:
        return Response(
            {'confirmation_code': 'Неверный код'},
            status=status.HTTP_400_BAD_REQUEST
        )
    token = AccessToken.for_user(user)
    return Response({'token': f'{token}'}, status=status.HTTP_200_OK)
