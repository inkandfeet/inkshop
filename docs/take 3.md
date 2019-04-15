
Inkshop - a digital shop for users you love.
    Auth
        - Simple user authentication.
        - username+pass -> jwt/keypair.
    
    inkdb/inkvault
        - Secure, encrypted user data storage that's easy to use and impossible to mess up.
        - Includes user product info.

    Store
        - Sell and deliver digital products
        - Integrates with (mostly powered by) Stripe
        - Simple reporting
        - Product
            info
            purchase email sent

    Downloads
        - unique link per user, proxy download content via inkdots proxy.

    Courses
        - unique link per user, auth is handled by course. (?) (Or, just link to the course?)

    Integrate
        - Securely report purchases to inkmail (webhook, public/priv key signing).
        - Add purchase info to inkvault


Inkmail
    Mailing lists for people you actually like.  Maybe even love.
    - Active, positive consent - beyond double-opt-in.
    - Auto-unsubscribe  (Please see consent, positive.)
    - No open tracking.
    - No click tracking.
    - No HTML templates
    - No automated sequences
    - No segments.  (Only confirmed subscriptions. Please see consent, active.)
    - no cookies, no logins, nothing.  No GDPR issues, and no silly cookie consent popups.

    Know what your readers loved
    - active, <3 feedback baked in.
    - 

    - Messages from people, not robots.
    - Can customize first name only.
    - Basic Markdown support (bold, italic, links only.)
    - Emoji support

    Securely Integrated
    - Can securely receive and store information about user purchases and context from other systems (Stripe, Inkshop, etc).
    - User emails never leave the system, are stored encrypted, and are only decrypted when sending.

    - Within the reply interface, can use email to look up if a person has purchased products.

    Good for business
    - Stop acting like a spammer, and start landing in people's inboxes.
    - Email that people actually want to open.

    Treat email like sleeping with someone.  "Yes" once doesn't mean "yes" forever.
    Be real.
    Show up.
    Don't be a stalker.

    Human Replies
    - See replies, reply from interface.
    - Context - all conversations from this person
    - Context - if they've made purchases from you (stripe, inkshop), you'll know.


Inkdots
    - anonymous analytics for pages, not people.
    - <3 -based.  Know what your visitors _loved_, not just what they saw.
    - short urls
    - No tracking. No cookies.  No creepy behavior.
    - GDPR compliant - with no silly cookie popups.


Inkblock
    - fast, compliant static websites.

    powers:
        inkandfeet.com
        all courses (individual instances?) (or just inkandfeet.com/twoyearlifeplan  inkandfeet.com/changemonsters?  inkandfeet.com/courses)
            - inkvault/inkdb included on every page
            - powered by vuejs/inkdb.  Render fine with no cookies/localstorage set, etc.
            - If login cookie set, renders differently, allows product access.
            - if not set, provide a "log in" link that can log user in and set token.
        downloads:
            - 


Inkdb/Inkvault
    - Or built on kinto?
    - Encryption wrapper for firestore