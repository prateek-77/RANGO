from django.http import HttpResponse
from django.template import RequestContext
from django.shortcuts import render_to_response
from rango.models import Category, Page
from rango.forms import CategoryForm, PageForm, UserForm, UserProfileForm
from django.contrib.auth import authenticate, login
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout

def index(request):
    request.session.set_test_cookie()
    # Request the context of the request.
    # The context contains information such as the client's machine details, for example
    context = RequestContext(request)
    # Construct a dictionary to pass to the template engineas its context.
    # Note the key boldmessage is same as that in the template.
    category_list = Category.objects.order_by('-name')[:5]
    pages_list = Page.objects.order_by('views')[:5]
    context_dict = {'categories': category_list, 'page_list': pages_list}
    # Return a rendered response to send to the client.
    # We make use of the shortcut function to make our lives easier.
    # Note that the first parameter is the template we wish to use.
    for category in category_list:
        category.url = category.name.replace(' ', '_')
    return render_to_response('rango/index.html', context_dict, context)


def about(request):
    context = RequestContext(request)
    context_dict_1 = {'boldmessage' : 'ABOUT PAGE'}
    return render_to_response('rango/about.html', context_dict_1, context)

def category(request, category_name_url):
    context = RequestContext(request)
    category_name = category_name_url.replace('_', ' ')
    context_dict = {'category_name' : category_name}

    try:
        category = Category.objects.get(name=category_name)
        pages = Page.objects.filter(category= category)
        context_dict['pages']=pages
        context_dict['category'] = category
        context_dict['category_name_url'] = category_name_url


    except Category.DoesNotExist:
        pass

    return render_to_response('rango/category.html', context_dict, context)


def add_category(request):
    context = RequestContext(request)

    if request.method == "POST":
        form = CategoryForm(request.POST)
        if form.is_valid():
            form.save(commit = True)
            return index(request)

        else:
            print(form.errors)
    else:
# If the request was not a POST, display the form to enter details.
        form = CategoryForm()
    return render_to_response('rango/add_category.html', {'form': form}, context)

def add_page(request, category_name_url):
    context = RequestContext(request)

    if request.method == "POST":
        form = PageForm(request.POST)
        if form.is_valid():
            page = form.save(commit = False)
            cat = Category.objects.get(name=category_name)
            page.category = cat
            page.views = 0
            page.likes = 0
            page.save()
            return category(request, category_name_url)

        else:
            print(form.errors)

    else:
        form = PageForm()
    return render_to_response( 'rango/add_page.html', {'category_name_url': category_name_url,  'form': form}, context)


def register(request):
    if request.session.test_cookie_worked():
        print(">>>> TEST COOKIE WORKED! Life is so beautiful.")
        request.session.delete_test_cookie()
    context = RequestContext(request)
    registered = False
    if request.method == 'POST':
        user_form = UserForm(data=request.POST)
        profile_form = UserProfileForm(data=request.POST)

        if user_form.is_valid() and profile_form.is_valid():
            user = user_form.save
            user.set_password(user.password)
            user.save()

            profile = profile_form.save(commit=False)
            profile.user = user

            if 'picture' in request.FILES:
                profile.picture = request.FILES['picture']

            profile.save()
            registered = True

        else:
            print(user_form.errors, profile_form.errors)

    else:
        user_form = UserForm()
        profile_form = UserProfileForm()

    return render_to_response('rango/register.html', {'user_form': user_form, 'profile_form': profile_form, 'registered': registered}, context)

def user_login(request):
    # Like before, obtain the context for the user's request.
    context = RequestContext(request)
    # If the request is a HTTP POST, try to pull out the relevant information.
    if request.method == 'POST':
        # Gather the username and password provided by the user.
        # This information is obtained from the login form.
        username = request.POST['username']
        password = request.POST['password']
        # Use Django's machinery to attempt to see if the username/password
        # combination is valid - a User object is returned if it is.
        user = authenticate(username=username, password=password)
        # If we have a User object, the details are correct.
        # If None (Python's way of representing the absence of a value), no user
        # with matching credentials was found.
        if user is not None:
            # Is the account active? It could have been disabled.
            if user.is_active:
                # If the account is valid and active, we can log the user in.
                # We'll send the user back to the homepage.
                login(request, user)
                return HttpResponseRedirect('/rango/')
            else:
                # An inactive account was used - no logging in!
                return HttpResponse("Your Rango account is disabled.")
        else:
            # Bad login details were provided. So we can't log the user in.
            print("Invalid login details: {0}, {1}".format(username, password))
            return HttpResponse("Invalid login details supplied.")
    # The request is not a HTTP POST, so display the login form.
    # This scenario would most likely be a HTTP GET.
    else:
        # No context variables to pass to the template system, hence the
        # blank dictionary object...
        return render_to_response('rango/login.html', {}, context)

@login_required
def restricted(request):
    return HttpResponse("Since you're logged in, you can see this text!")


@login_required
def user_logout(request):
    # Since we know the user is logged in, we can now just log them out.
    logout(request)
    # Take the user back to the homepage.
    return HttpResponseRedirect('/rango/')
