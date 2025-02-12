from rest_framework import status, permissions
from rest_framework.viewsets import ModelViewSet
from .models import User, Genre, Book, Borrowing, Fine
from django.contrib.auth.models import Group
from .serializers import UserSerializer, BookSerializer, GenreSerializer, BorrowingSerializer, FineSerializer, GroupSerializer
from rest_framework.response import Response
from django.contrib.auth.hashers import make_password
from rest_framework.decorators import api_view, permission_classes
from django.contrib.auth import authenticate
from rest_framework.authtoken.models import Token

# Create your views here.


class GenreViewSet(ModelViewSet):
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer


class BookViewSet(ModelViewSet):
    queryset = Book.objects.all()
    serializer_class = BookSerializer

    # Filtering and searching using title, author and genre
    filterest_fields = ['title', 'author', 'genre__name']
    search_fields = ['title', 'author', 'genre__name']


class BorrowingViewSet(ModelViewSet):
    queryset = Borrowing.objects.all()
    serializer_class = BorrowingSerializer
    # Filtering By username and due date
    filterset_fields = ['member__username', 'due_date']
    # Searching for members by username
    search_fields = ['member__username']

    def create(self, request):
        data = request.data.copy()
        # Auto Asign Value Of member to Current User
        data["member"] = request.user.id
        serializer = self.get_serializer(data=data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class FineViewSet(ModelViewSet):
    queryset = Fine.objects.all()
    serializer_class = FineSerializer


# Api View for Viewing Groups
@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def group_api_view(request):
    group_objs = Group.objects.all()
    serializer = GroupSerializer(group_objs, many=True)

    return Response(serializer.data)


# Api View for Registering new User
@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def register_api_view(request):

    # Only allow to Register new User If The Group of Current User Is Admin
    if request.user.groups.name == 'Admin':
        # Hashing Of Password for Better Security
        # Get PassWord from request - UnHashed
        password = request.data.get('password')
        hash_password = make_password(password)  # Hash pashword Using sHa
        # Make copy of Requested data for Changing Password to Hash Password
        data = request.data.copy()
        data['password'] = hash_password  # Change Password to  hash password
        serializer = UserSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # If User Group is not admin Returns Permiission Error
    else:
        return Response({'detail': 'You do not have permissions'}, status=status.HTTP_403_FORBIDDEN)


# Api View for login User
@api_view(['POST'])
@permission_classes([])
def login_api_view(request):

    # get Email And Password From request data and stoore it in variables email and password
    email = request.data.get('email')
    password = request.data.get('password')

    # Check if Request data Matches The Values in Stored Data
    user = authenticate(username=email, password=password)

    # if User is not authenticated then either email or password are invalid
    if user == None:
        return Response({'detail': 'Invalid Credentials!'}, status=status.HTTP_400_BAD_REQUEST)

    # Get Token If The Token of Logged in user is avaiilable Else Create New Token For The User
    token, _ = Token.objects.get_or_create(user=user)

    return Response(token.key)
