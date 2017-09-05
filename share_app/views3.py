from django.shortcuts import render

def rateUser(request):
	if request.POST:
		if request.user.is_authenicated():
			userRating.rater = Member.objects.get(username = request.user.username)
			userRating.user = Member.objects.get(id = request.POST['user'])
			userRating.rating= request.POST['rating']
		return HttpResponseRedirect('/share_app/')