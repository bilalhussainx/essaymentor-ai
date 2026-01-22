"""
Views for vector database API endpoints.
"""

from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .services import get_vectordb_service


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def search_essays(request):
    """
    POST /api/vectordb/search/

    Search for similar essays in the vector database.

    Request body:
    {
        "query": "coding journey and learning",
        "n_results": 5,
        "min_score": 7.5,
        "filter": {
            "university": "MIT"
        }
    }

    Response:
    {
        "results": [
            {
                "id": "essay_1",
                "text": "...",
                "metadata": {
                    "topic": "coding",
                    "score": 9.0,
                    "university": "MIT"
                },
                "similarity": 0.87
            }
        ],
        "count": 5
    }
    """
    query = request.data.get('query')
    if not query:
        return Response(
            {'error': 'query is required'},
            status=status.HTTP_400_BAD_REQUEST
        )

    n_results = request.data.get('n_results', 5)
    min_score = request.data.get('min_score', 7.5)
    filter_metadata = request.data.get('filter')

    service = get_vectordb_service()
    results = service.search_similar(
        query=query,
        n_results=n_results,
        min_score=min_score,
        filter_metadata=filter_metadata
    )

    return Response({
        'results': results,
        'count': len(results)
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_stats(request):
    """
    GET /api/vectordb/stats/

    Get vector database statistics.

    Response:
    {
        "total_essays": 150,
        "topics": {
            "coding": 45,
            "immigration": 32,
            "leadership": 28
        },
        "average_score": 8.4,
        "score_range": [7.5, 9.5]
    }
    """
    service = get_vectordb_service()
    stats = service.get_stats()
    return Response(stats)
