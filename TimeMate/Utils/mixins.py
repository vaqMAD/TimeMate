from TimeMate.Serializers.user_serializers import UserSerializer

class OwnerRepresentationMixin:
    def to_representation(self, instance):
        representation = super().to_representation(instance)
        # Check if the instance has an `owner`
        if hasattr(instance, 'owner'):
            # Return owner field as a nested serialized object, not as an ID
            representation['owner'] = UserSerializer(instance.owner).data
        return representation
