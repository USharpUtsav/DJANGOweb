from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login
from django.contrib import messages
from django.contrib.auth.models import User
from .forms import RegistrationForm, LoginForm, ResetPasswordForm, PostForm, CommentForm, NewPasswordForm
from django.contrib.auth.decorators import login_required
from .models import Post, Comment
from django.utils import timezone
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from django.http import JsonResponse
import numpy as np
import pickle
from nltk.tokenize import word_tokenize
from deep_translator import GoogleTranslator
from langdetect import detect
from nltk.sentiment.vader import SentimentIntensityAnalyzer




try:
    # Load GloVe embeddings
    with open(r"D:\7thsemproject\MAINPROJECTFOLDER\glove_embeddings.pkl", "rb") as f:
        glove_embeddings = pickle.load(f)
    print("GloVe embeddings loaded successfully.")
except Exception as e:
    print(f"Error loading GloVe embeddings: {e}")

try:
    # Load label encoder
    with open(r"D:\7thsemproject\MAINPROJECTFOLDER\label_encoder.pkl", "rb") as f:
        label_encoder = pickle.load(f)
    print("Label encoder loaded successfully.")
except Exception as e:
    print(f"Error loading label encoder: {e}")

try:
    # Load sentiment model
    with open(r"D:\7thsemproject\MAINPROJECTFOLDER\sentiment_model.pkl", "rb") as f:
        model4 = pickle.load(f)
    print("Sentiment model loaded successfully.")
except Exception as e:
    print(f"Error loading sentiment model: {e}")



def register(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)  # Log in the user immediately after registration
            messages.success(request, 'Registration successful! You are now logged in.')
            return redirect('home')  # Redirect to the home page
        else:
            messages.error(request, 'Registration failed. Please correct the errors below.')
    else:
        form = RegistrationForm()

    return render(request, 'register.html', {'form': form})

# View for user login
def user_login(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, "Login successful!")
                return redirect('home')  # Redirect to home page after successful login
            else:
                messages.error(request, "Invalid username or password.")
    else:
        form = LoginForm()

    return render(request, 'login.html', {'form': form})

# View for resetting password
def reset_password(request):
    if request.method == 'POST':
        form = ResetPasswordForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            favorite_food = form.cleaned_data['favorite_food']

            try:
                user = User.objects.get(username=username)
            except User.DoesNotExist:
                messages.error(request, "No user found with this username.")
                return render(request, 'reset_password.html', {'form': form})

            if user.first_name == favorite_food:
                # Proceed to reset password logic here
                messages.success(request, "Verification successful! You can reset your password.")
                return redirect('new_password')  # Redirect to a page for entering a new password
            else:
                messages.error(request, "Favorite food does not match.")
    else:
        form = ResetPasswordForm()

    return render(request, 'reset_password.html', {'form': form})

def home(request):
    posts = Post.objects.all().order_by('-created_at')
    return render(request, 'home.html', {'posts': posts})

@login_required
def create_post(request):
    if request.method == 'POST':
        form = PostForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            return redirect('home')
    else:
        form = PostForm()

    return render(request, 'create_post.html', {'form': form})


def add_comment(request, post_id):
    if request.method == 'POST':
        post = get_object_or_404(Post, id=post_id)
        content = request.POST.get('comment')
        comment = Comment.objects.create(post=post, content=content, author=request.user)

        # Prepare data to return
        data = {
            'author': comment.author.username,
            'content': comment.content,
            'created_at': comment.created_at.strftime('%Y-%m-%d %H:%M:%S'),
        }

        return JsonResponse(data)
    return JsonResponse({'error': 'Invalid request'}, status=400)


@login_required
def my_posts(request):
    posts = Post.objects.filter(author=request.user)
    return render(request, 'my_posts.html', {'posts': posts})

from django.contrib.auth import logout

def logout_view(request):
    logout(request)
    messages.success(request, 'You have been logged out.')
    return redirect('login')  # Redirect to login page

def new_password(request):
    if request.method == 'POST':
        form = NewPasswordForm(request.POST)
        if form.is_valid():
            new_password = form.cleaned_data['new_password']
            username = request.user.username
            user = User.objects.get(username=username)
            user.set_password(new_password)
            user.save()
            messages.success(request, "Your password has been updated successfully!")
            return redirect('login')  # Redirect to the login page after resetting
    else:
        form = NewPasswordForm()

    return render(request, 'new_password.html', {'form': form})


##SENTIMENT ANALYSIS
def translate_nepali_to_english(nepali_text):
    try:
        translation = GoogleTranslator(source='ne', target='en').translate(nepali_text)
        return translation
    except Exception as e:
        print(f"Translation failed: {e}")
        return nepali_text  # Fallback to original text if translation fails


def sentence_to_embedding(sentence, embeddings):
    # Ensure the input is a valid string; if not, convert it to an empty string
    if not isinstance(sentence, str):
        sentence = ""

    # Tokenize the sentence using NLTK's word_tokenize for consistency
    words = word_tokenize(sentence)

    # Get embeddings for each valid word
    valid_embeddings = [embeddings[word] for word in words if word in embeddings]

    # If there are valid embeddings, return their mean; otherwise, return a zero vector
    if valid_embeddings:
        return np.mean(valid_embeddings, axis=0)
    else:
        return np.zeros(100)  # Assuming GloVe is 100-dimensional

def vader_sentiment_features(sentence):
    analyzer = SentimentIntensityAnalyzer()
    sentiment_dict = analyzer.polarity_scores(sentence)
    return [sentiment_dict['neg'], sentiment_dict['neu'], sentiment_dict['pos'], sentiment_dict['compound']]



def predict_sentiment(new_sentence):
    try:
        language = detect(new_sentence)
        if language == 'ne':
            translated_sentence = translate_nepali_to_english(new_sentence)
        else:
            translated_sentence = new_sentence
    except Exception as e:
        print(f"Language detection failed: {e}")
        translated_sentence = new_sentence

    # Get the GloVe feature (now 100d)
    glove_feature = sentence_to_embedding(translated_sentence, glove_embeddings).reshape(1, -1)
    print("GloVe feature shape:", glove_feature.shape)

    # Get the VADER sentiment features
    vader_feature = np.array(vader_sentiment_features(translated_sentence)).reshape(1, -1)
    print("VADER feature shape:", vader_feature.shape)

    # Combine GloVe and VADER features
    combined_feature = np.hstack([glove_feature, vader_feature])
    print("Combined feature shape:", combined_feature.shape)

    # Make a prediction using the model
    prediction = model4.predict(combined_feature)

    # If prediction returns probabilities, convert to class labels
    if prediction.ndim > 1:
        predicted_classes = np.argmax(prediction, axis=1).ravel()  # Flatten the array
    else:
        predicted_classes = np.array([prediction]).ravel()  # Ensure it's 1D

    # Use label encoder to get the original labels
    predicted_label = label_encoder.inverse_transform(predicted_classes)

    return predicted_label[0]


def analyze_sentiment(request):
    if request.method == 'POST' and request.headers.get('x-requested-with') == 'XMLHttpRequest':
        post_id = request.POST.get('post_id')
        post = Post.objects.get(id=post_id)
        comments = Comment.objects.filter(post=post)

        # Collect comment texts
        comment_texts = [comment.content for comment in comments]
        print("Comment texts:", comment_texts)  # Debugging line

        # Run sentiment analysis on each comment
        sentiments = [predict_sentiment(text) for text in comment_texts]
        print("Sentiments:", sentiments)  # Debugging line

        # Count the sentiments with matching keys
        sentiment_counts = {
            'Positive': sentiments.count('Positive'),
            'Neutral': sentiments.count('Neutral'),
            'Negative': sentiments.count('Negative')
        }
        print("Sentiment counts:", sentiment_counts)  # Debugging line

        # Determine overall sentiment
        if sentiment_counts['Positive'] > sentiment_counts['Negative'] and sentiment_counts['Positive'] > sentiment_counts['Neutral']:
            overall_sentiment = "Positive"
        elif sentiment_counts['Negative'] > sentiment_counts['Positive'] and sentiment_counts['Negative'] > sentiment_counts['Neutral']:
            overall_sentiment = "Negative"
        else:
            overall_sentiment = "Neutral"

        return JsonResponse({'sentiment': overall_sentiment})

    return JsonResponse({'error': 'Invalid request'}, status=400)



