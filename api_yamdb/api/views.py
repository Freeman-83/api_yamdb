from django.shortcuts import get_object_or_404
from rest_framework import viewsets

from ..reviews.models import Review
from .permissions import IsAdminModeratorOwnerOrReadOnly
from .serializers import CommentSerializer, ReviewSerializer


class ReviewViewSet(viewsets.ModelViewSet):
    serializer_class = ReviewSerializer
    permission_classes = (IsAdminModeratorOwnerOrReadOnly,)
    # queryset =


class CommentViewSet(viewsets.ModelViewSet):
    serializer_class = CommentSerializer
    permission_classes = (IsAdminModeratorOwnerOrReadOnly,)

    def get_queryset(self):
        review = get_object_or_404(Review, pk=self.kwargs.get('review_id'))
        return review.comments.select_related('author').all()

    def perform_create(self, serializer):
        review = get_object_or_404(
            Review, id=self.kwargs.get('title_id'),
            title=self.kwargs.get('review_id')
        )
        serializer.save(author=self.request.user, review=review)
