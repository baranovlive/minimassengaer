from django.contrib.auth.decorators import login_required, permission_required
from django.shortcuts import render
from django.urls import reverse
from django.utils.safestring import mark_safe
from django.contrib.auth.models import User

from .models import Room, Message

from django.http import HttpResponseRedirect
from dataclasses import dataclass
from django.db.models.query import QuerySet

import time
import json


@dataclass
class DialogData:
    room_name: str
    last_message_content: str
    last_message_send_date: str
    user: QuerySet


@login_required
def chat_choice(request):
    context = {
        'page': 2,
        'page_title': 'Диалоги',
    }
    room_name_and_user = list()
    unique_rooms = list()
    if request.user.is_superuser:
        rooms_qs = Room.objects.exclude(name=request.user.username).order_by('-message__send_date')
        for i, room in enumerate(rooms_qs):
            try:
                msg_content = room.message.last().content
                msg_date = room.message.last().send_date
            except:
                msg_content = ''
                msg_date = ''
            room_name_and_user.append(
                DialogData(
                    room_name=room.name,
                    last_message_content=msg_content,
                    last_message_send_date=msg_date,
                    user=room.user_simple
                )
            )

            if room_name_and_user[i] not in unique_rooms:
                unique_rooms.append(room_name_and_user[i])
    else:
        try:
            room = Room.objects.get(name=request.user.username)
        except:
            return render(request, 'Chat/chat_choice.html', context)
        try:
            msg_content = room.message.last().content
            msg_date = room.message.last().send_date
        except:
            msg_content = ''
            msg_date = ''
        unique_rooms.append(
            DialogData(
                room_name=room.name,
                last_message_content=msg_content,
                last_message_send_date=msg_date,
                user=room.user_admin
            )
        )

    context['room_name_and_user'] = unique_rooms
    return render(request, 'Chat/chat_choice.html', context)


@permission_required('polls.can_vote')
def distribution(request):
    if request.user.is_superuser:
        users = User.objects.exclude(is_superuser=True)
    else:
        users = User.objects.filter(username=request.user)

    context = {
        'page': 2,
        'page_title': 'Групповая рассылка',
        'users': users,
    }
    return render(request, 'Chat/distribution.html', context)


@permission_required('polls.can_vote')
def save_distribution(request):
    try:
        content = request.POST['content']
    except:
        content = ''
    users = request.POST.getlist('search')
    user_admin = User.objects.get(is_superuser=True)
    for user in users:
        author = User.objects.get(username=user_admin)
        try:
            current_room = Room.objects.get(name=user)
        except Room.DoesNotExist:
            user = User.objects.get(username=user)
            Room.objects.create(name=user.username, user_simple=user,
                                user_admin=author)
            current_room = Room.objects.get(name=user)
        Message.objects.create(content=content, author=author, room=current_room)
    return HttpResponseRedirect(reverse('Chat:chat_choice'))


@login_required
def room(request, room_name):
    # Get user and user_admin
    try:
        user = User.objects.get(username=room_name)
        user_admin = User.objects.get(is_superuser=True)
    except User.DoesNotExist:
        return False
    # Get current_room or create
    try:
        current_room = Room.objects.get(name=room_name)
    except Room.DoesNotExist:
        Room.objects.create(name=room_name, user_simple=user,
                            user_admin=user_admin)
        current_room = Room.objects.get(name=room_name)
    try:
        messages = current_room.message.all()
    except:
        messages = None

    if request.user == user_admin:
        if user.first_name != '' and user.last_name != '':
            page_title = f'{user.first_name} {user.last_name}'
        else:
            page_title = user.username
    elif request.user == user:
        if user_admin.first_name != '' and user_admin.last_name != '':
            page_title = f'{user_admin.first_name} {user_admin.last_name}'
        else:
            page_title = user_admin.username
    context = {
        'page_title': page_title,
        'messages': messages,
        'current_room_name': mark_safe(json.dumps(current_room.name)),
        'room_name_json': mark_safe(json.dumps(user.username)),
        'current_user': mark_safe(json.dumps(request.user.username)),
        'username': mark_safe(json.dumps(user.username)),
    }

    return render(request, 'Chat/room.html', context)


@permission_required('polls.can_vote')
def delete_room(request, room_name):
    try:
        room = Room.objects.get(name=room_name)
        room.delete()
    except Room.DoesNotExist:
        pass
    return HttpResponseRedirect(reverse('Chat:chat_choice'))
