
from rest_framework import serializers

from .models import Ad, ExchangeProposal

class AdSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ad
        fields = '__all__'
        read_only_fields = ['user', 'created_at']

class ExchangeProposalSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExchangeProposal
        fields = '__all__'
        read_only_fields = ['ad_sender', 'status', 'created_at']

    def validate(self, data):
        
        if data['ad_receiver'] == self.context['request'].user.ad:
            raise serializers.ValidationError("Нельзя создать предложение на своё объявление")
        return data

    def create(self, validated_data):
        
        validated_data['ad_sender'] = self.context['request'].user.ad
        return super().create(validated_data)