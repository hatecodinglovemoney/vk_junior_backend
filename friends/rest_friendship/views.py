from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from friendship.exceptions import AlreadyExistsError
from friendship.exceptions import AlreadyFriendsError
from friendship.models import Friend
from friendship.models import FriendshipRequest
from rest_framework import status
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .serializers import FriendSerializer
from .serializers import FriendshipRequestResponseSerializer
from .serializers import FriendshipRequestSerializer

User = get_user_model()


class FriendViewSet(viewsets.ModelViewSet):
    """
    ViewSet.
    """
    permission_classes = (IsAuthenticated,)
    serializer_class = FriendSerializer
    lookup_field = 'pk'

    def list(self, request):
        """
        Список друзей.
        """
        friend_requests = Friend.objects.friends(user=request.user)
        self.queryset = friend_requests
        self.http_method_names = ['get', 'head', 'options', ]
        return Response(FriendSerializer(friend_requests, many=True).data)

    @action(detail=False)
    def requests(self, request):
        """
        Список входящих заявок.
        """
        friend_requests = Friend.objects.unrejected_requests(user=request.user)
        self.queryset = friend_requests
        return Response(
            FriendshipRequestSerializer(friend_requests, many=True).data)

    @action(detail=False)
    def rejected_requests(self, request):
        """
        Список отклоненных пользователем заявок.
        """
        friend_requests = Friend.objects.rejected_requests(user=request.user)
        self.queryset = friend_requests
        return Response(
            FriendshipRequestSerializer(friend_requests, many=True).data)

    @action(detail=False)
    def sent_requests(self, request):
        """
        Список исходящих заявок.
        """
        friend_requests = Friend.objects.sent_requests(user=request.user)
        self.queryset = friend_requests
        return Response(
            FriendshipRequestSerializer(friend_requests, many=True).data)

    @action(detail=False)
    def get_status(self, request, username=None):
        """
        Получение статуса:
        - Входящая заявка
        - Исходящая заявка
        - В друзьях
        - None
        """
        username = request.data.get('username')
        if not username:
            return Response(
                {'message': "Введите корректное имя пользователя."},
                status=status.HTTP_400_BAD_REQUEST
            )
        requested_user = get_object_or_404(User, username=username)
        if Friend.objects.are_friends(request.user, requested_user):
            return Response({'message': 'Пользователь у вас в друзьях.'})
        elif FriendshipRequest.objects.filter(
                from_user=requested_user, to_user=request.user
        ).exists():
            return Response(
                {'message': 'Пользователь у вас во входящих заявках.'}
            )
        elif FriendshipRequest.objects.filter(
                from_user=request.user, to_user=requested_user
        ).exists():
            return Response(
                {'message': 'Пользователь у вас в исходящих заявках.'}
            )
        else:
            return Response(
                {'message': "None."},
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(
        detail=False,
        serializer_class=FriendshipRequestSerializer,
        methods=['post']
    )
    def add_friend(self, request, username=None):
        """
        Добавление нового друга с данными POST:
        - to_user
        - message
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        to_user = get_object_or_404(
            User,
            username=serializer.validated_data.get('to_user')
        )
        from_user = request.user
        try:
            friend_request = FriendshipRequest.objects.get(
                from_user=to_user, to_user=from_user, rejected__isnull=True
            )
            friend_request.accept()
            return Response(
                {'message': 'Дружба подтверждена'},
                status.HTTP_201_CREATED
            )
        except FriendshipRequest.DoesNotExist:
            pass
        try:
            friend_obj = Friend.objects.add_friend(
                # The sender
                from_user,
                # The recipient
                to_user,
                # Message (...or empty str)
                message=request.data.get('message', '')
            )
            return Response(
                FriendshipRequestSerializer(friend_obj).data,
                status.HTTP_201_CREATED
            )
        except (AlreadyExistsError, AlreadyFriendsError) as e:
            return Response(
                {"message": str(e)},
                status.HTTP_400_BAD_REQUEST
            )

    @action(
        detail=False,
        serializer_class=FriendshipRequestSerializer,
        methods=['post']
    )
    def remove_friend(self, request):
        """
        Удаление друга.

        Имя пользователя, указанное в запросе,
        будет удалено из текущих друзей пользователя.
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        to_user = get_object_or_404(
            User,
            username=serializer.validated_data.get('to_user')
        )

        if Friend.objects.remove_friend(request.user, to_user):
            message = 'Друг удален.'
            status_code = status.HTTP_204_NO_CONTENT
        else:
            message = 'Друг не найден.'
            status_code = status.HTTP_400_BAD_REQUEST

        return Response(
            {"message": message},
            status=status_code
        )

    @action(detail=False,
            serializer_class=FriendshipRequestResponseSerializer,
            methods=['post'])
    def accept_request(self, request, id=None):
        """
        Одобрение заявки в друзья.

        Указанный идентификатор запроса будет принят.
        """
        id = request.data.get('id', None)
        friendship_request = get_object_or_404(
            FriendshipRequest, pk=id)

        if not friendship_request.to_user == request.user:
            return Response(
                {"message": "Запрос для текущего пользователя не найден."},
                status.HTTP_400_BAD_REQUEST
            )

        friendship_request.accept()
        return Response(
            {"message": "Заявка принята, пользователь добавлен в друзья."},
            status.HTTP_201_CREATED
        )

    @action(detail=False,
            serializer_class=FriendshipRequestResponseSerializer,
            methods=['post'])
    def reject_request(self, request, id=None):
        """
        Отклонение заявки в друзья.

        Указанный идентификатор запроса будет отклонен.
        """
        id = request.data.get('id', None)
        friendship_request = get_object_or_404(
            FriendshipRequest, pk=id)
        if not friendship_request.to_user == request.user:
            return Response(
                {"message": "Запрос для текущего пользователя не найден."},
                status.HTTP_400_BAD_REQUEST
            )

        friendship_request.reject()

        return Response(
            {"message": "Запрос отклонен, пользователь НЕ добавлен в друзья."},
            status.HTTP_201_CREATED
        )
