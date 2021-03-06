# Inkshop

Simple stores and hosting for digital products.

Sell and provide access to digital products - both downloads and ones you're hosting, all from a single domain.

(?) Authentication and encrypted storage for users to save data using your products, automatically included. (via by [inkDB](https://github.com/inkandfeet/inkdb))
(Need to decide the best way to integrate this.)

Turn-key integration with Stripe.

All the user-friendly things you'd expect.  Password reset, two-factor authentication, GDPR compliance.


Tech: 
- current inkdots proxy under the hood, routing content from a statically hosted site.
- an authorized, inkdb included into any HTML pages.



Inkshop - a digital shop for users you love.

    Auth
        - Simple user authentication.
        - username+pass -> jwt/keypair.
    
    Vault
        - Secure, encrypted user data storage that's easy to use and impossible to mess up.

    Store
        - Sell and deliver digital products
        - Integrates with Stripe
        - Simple reporting
        - Product
            info
            purchase receipt

    Integrate
        - Securely report purchases to letters/other systems (webhook).
