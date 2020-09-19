from rest_framework import viewsets, mixins
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
# internal
from . import serializers

from core.models import Tag


class TagView(viewsets.GenericViewSet,
              mixins.ListModelMixin,
              mixins.CreateModelMixin):
    serializer_class = serializers.TagSerializer
    permission_classes = (IsAuthenticated, )
    authentication_classes = (TokenAuthentication,)
    queryset = Tag.objects.all()

    def get_queryset(self):
        return self.queryset.filter(user=self.request.user).order_by('-name')

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
