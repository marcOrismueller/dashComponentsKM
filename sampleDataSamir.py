'''
I. DASH COMPONENTS
    Application is for kitchen chefs. In a restaurant, food is served in multiple gears (in German called “Gang”),
    in most of the times we have 1., 2. & 3. Gang

    The task is to make the phrase “1. Gang / 2. Gang / 3. Gang” clickable, and all corresponding subelements are
    crossed out in the CardBody & subtracted from ListGroup on the left [THIS IS THE MOST IMPORTANT FEATURE TO ADD!!!]

    Additional Filter needs to be added for “1. 2. 3. Gang” in the FILTER modal, but no necessity for the pitch on
    monday

    The prices for each meal are shown as well, so we don't have to split the string into substring before every number,
    but before every number followed by an x (First string from card_body_input as example). Instead of a '+' as a bonus
    information we do have a '#' now:

    1. Gang
        1x Hühner-Kokosnuss-Suppe 8.50
        1x Karotten-Ingwer-Suppe 4.50
        1x Ribollita 6.50

    2. Gang
        1x Caesar Salat 10.00
        1x Chef Salat 10.00
            # French Dressing
        1x Chef Salat 10.00
            # American Dressing


II. CSS COMPONENTS
    As discussed, the goal is to use the full width of the page with the ListGroup on the left, & four cards in a row

    Change the 'SUBTRACT' button to a toggle button to 'Start' (green) & 'Finished' (red)
    If 'Start' is clicked the card should have a green border, if finished is clicked it should have the same
    functionality as it does right now

    If 'Start' is not yet clicked, the everything besides the card footer with the button should be disabled / look like
    not clickable

III. LAUNCH & WORKING TOGETHER
    Launch a sample application to Heroku for the presentation on monday, that potential customers can test some features,
    I have time every night now until Saturday, there the app has to be launched

IV. NEXT TASKS FOR THIS PROJECT (STARTING NEXT WEEK HOPEFULLY)
    . REGEX - I need to work on some Printer Manipulation Stuff & the "Regex Pipeline"
    . DATABASE - We need to discuss the database structure, Dash States, & where to host / launch the full application
    . DASH - Refine existing components & add some minor features too


V. THE BORING STUFF
    I will talk to the partners next week regarding your role in the company. This right now is a smaller project to
    start and to build a much broader platform out of this tool. Furthermore we have a real AI project coming along,
    hopefully in two to three months. I want to work a lot with Python Dash and a lot with you too,
     so I think you will have a lot of fun :D!

    I think you want to work with me on these challenges, but we have to do a contract because of your compensation then.
    So feel free to think about your salary per hour & how many hours a week you want to work with me, & then I'd say
    let's make history :P
'''


card_header_input = [
    '16-Mar-21 13:15 Hypersoft 7',
    '16-Mar-21 13:15 Hypersoft 9',
]

card_body_input = [
    '1. Gang 1x Hühner-Kokosnuss-Suppe 8.50 1x Karotten-Ingwer-Suppe 4.50 1x Ribollita 6.50 2. Gang 1x Caesar Salat 10.00 1x Chef Salat 10.00 French Dressing 1x Chef Salat 10.00 American Dressing',
    '3. Gang 1x Burger Royal 21.00 # Bratkartoffel # extra Champignon + 1.50 Filet Steak 50.20 1x # 180 g 37,90 # Medium Rare (50øC) # Bratkartoffeln +4,90 # Kartoffelgratin +4,90 # Pepper Jus +2,50 Filet Steak 68.20 1x # 300 g 57,90 Medium Well (60øC) # Pommes +4,90 # Knoblauchbrot +2,90 # Sauce Bearnaise +2,50',
]