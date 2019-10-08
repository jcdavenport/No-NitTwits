import tweepy
from tweepy import OAuthHandler
import time
import json
import sys
import re

try:
    import config
except ModuleNotFoundError:
    print("No config.py file found!!!")
    print("""
-create a config.py file in this directory with 
 the following Twitter API OAuth data:

consumer_key = 'your-consumer-key'
consumer_secret = 'your-consumer-secret'
access_token = 'your-access-token'
access_secret = 'your-access-secret'
""")
    sys.exit()

auth = OAuthHandler(config.consumer_key, config.consumer_secret)
auth.set_access_token(config.access_token, config.access_secret)
api = tweepy.API(auth)


def menu():
    print()
    print("|*****************No NitTWITs*****************|")
    choice = ""
    try:
        choice = input("""
A: Enter Twitter Handle
B: Members I Follow
C: Remove Everyone I Follow
Q: Quit
    
select a letter: """)
    except KeyboardInterrupt:
        ender()
    print()

    if choice == "A" or choice == "a":
        get_handle()
    elif choice == "B" or choice == "b":
        friend_list()
    elif choice == "C" or choice == "c":
        destroy_friends()
    elif choice == "Q" or choice == "q":
        quitter()
    elif choice == "":
        print("Please select an option!")
        menu()
    else:
        print("You must only select either A, B, C, or Q.")
        print("Please try again!")
        time.sleep(2)
        menu()


def get_handle():
    # prompt user for handle to search for
    while True:
        try:
            # input validation
            handle = str(input("Enter a handle to search for: @"))
            if len(handle) < 1:
                raise EOFError()
            elif not re.match("[\\w]", handle) or len(handle) > 15:
                raise TypeError()
            break
        except TypeError:
            print("Invalid Twitter handle format!")
            print()
            time.sleep(2)
            handle = ""
            continue
        except EOFError:
            print("Handle cannot be blank!")
            print()
            time.sleep(2)
            continue
        except KeyboardInterrupt:
            ender()
        except Exception as e:
            print("Error: %s" % str(e))
            handle = ""
            continue

    get_list(handle)


def get_list(handle):
    try:
        # get all the lists for the user
        lists = api.lists_all(screen_name=handle)
    except Exception as e:
        print("Error: %s" % str(e))
        print("Check spelling, or try a different handle.")
        time.sleep(2)
        ender()

    print()
    print("Collecting lists owned by @%s" % handle)
    print()

    time.sleep(2)

    # used to determine list owner
    correct = "\"" + handle + "\""

    # initialize count for total list number
    count = 0

    # store the owned lists to be used as menu options
    opt = []

    # get the owned lists
    for l in lists:
        data = lists[count]

        # isolating the screen name from the raw data
        json_str = json.dumps(data._json)
        parsed = json.loads(json_str)
        owner = json.dumps(parsed['user']['screen_name'], indent=4, sort_keys=True)

        # only save a list name that the user created
        if owner == correct:
            a = json.dumps(parsed['name'], indent=4, sort_keys=True)
            a = a.strip('\"')
            opt.append(a)

        count += 1
    options(opt, handle)


def options(opts, sname):
    print("Select a list to follow it's members:")
    print()

    opt_num = 1
    for num in opts:
        print(opt_num, " - " + num)
        opt_num += 1

    print()
    choice = 0
    while True:
        try:
            choice = int(input("select a number: "))
            if not isinstance(choice, int) or choice == 0 or choice > opt_num:
                raise TypeError()
            break
        except TypeError:
            print("Invalid choice! Please try again.")
            print()
            time.sleep(2)
            continue
        except ValueError:
            print("Invalid choice! Please try again.")
            print()
            time.sleep(2)
            continue
        except KeyboardInterrupt:
            ender()
    print()

    opt_num = 1
    for lname in opts:
        if choice == opt_num:
            print("You selected %s," % lname)
            get_members(sname, lname)
            break
        else:
            opt_num += 1
    print()
    time.sleep(4)
    ender()


def get_members(sname, lname):
    # format list name for use in url
    li_name = lname.lower()
    li_name = li_name.replace(" - ", " ")
    li_name = li_name.replace(" ", "-")

    # for testing li_name #
    # print(sname, ":: " + li_name)
    # input("Press enter to continue...")
    # print()
    # ender()

    # get the members from the specified list
    list_mems = tweepy.Cursor(api.list_members, sname, li_name).items()

    # get a count of the member's you now follow from this list
    mc = follow(list_mems)

    print("Now following %d members from @%s's %s list!" % (mc, sname, lname))
    return


def follow(list_mems):
    member_count = 0

    for mems in list_mems:
        # isolating the screen name from the raw data
        j_str = json.dumps(mems._json)
        parsd = json.loads(j_str)
        l_member = json.dumps(parsd['screen_name'], indent=4, sort_keys=True)
        l_member = l_member.strip('\"')

        # create friendship with the authenticated user
        api.create_friendship(screen_name=l_member)
        member_count += 1

    return member_count


def friend_list():
    num_friends = 0
    for friend in tweepy.Cursor(api.friends).items():
        if friend:
            num_friends += 1
        else:
            break

    if num_friends == 0:
        print("You are not following any members yet!!")
    else:
        print("You are following %d members:" % num_friends)
        print()
        # iterate through list and print friends
        for friend in tweepy.Cursor(api.friends).items():
            # isolating the screen name from the raw data
            friend_str = json.dumps(friend._json)
            friend_parse = json.loads(friend_str)
            my_friends = json.dumps(friend_parse['screen_name'], indent=4, sort_keys=True)
            my_friends = my_friends.strip('\"')
            print("@%s" % my_friends)

    ender()


def destroy_friends():
    count = 0
    for friend in tweepy.Cursor(api.friends).items():
        # isolating the screen name from the raw data
        friend_str = json.dumps(friend._json)
        friend_parse = json.loads(friend_str)
        my_friend = json.dumps(friend_parse['screen_name'], indent=4, sort_keys=True)
        my_friend = my_friend.strip('\"')
        api.destroy_friendship(screen_name=my_friend)
        count += 1
    print()
    print("%d friends have been expunged!!" % count)
    time.sleep(2)
    ender()


def ender():
    print()
    nav = int(input("\nWhat would you like to do?\n(1=MainMenu, 0=Exit): "))
    if nav is 1:
        menu()
    elif nav is 0:
        print("Goodbye!")
        sys.exit()
    else:
        print("Pick either 1 or 0!")
        ender()
    

def quitter():
    print()
    q_ans = input("Are you sure you want to quit?(Y or N): ")
    if q_ans == "N" or q_ans == "n":
        menu()
    else:
        print("Goodbye!")
        sys.exit()


if __name__ == '__main__':
    menu()
