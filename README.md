# ContraceptEase
## On the way to make contraceptive alerts accesible

Did you know that, in Chile, contraception failure is no stranger?
More than 200 women were affected by this fenomenon on 2020 alone.
Did you also know that this information is not accesible easily for people who are blind or hard of sight?

That is where ContraceptEase comes in, we identified this problem and developed a simple yet effective solution that combines NFC technology and web apps.

By labeling contraceptives with an NFC tag, that withholds a url to our service, we can make contraceptives accesible. But, what is our service? 

Rooted in Python Flask we developed a fullstack accesible web app that queries the Chilean Health Services Web portal and _asks_ "Is this product in a sanitary alert?" Trough the portals answer (imported as a PDF to our program), we can obtain when and how many of these alerts where issued.
The we follow the embedded links on the alerts obtaining the most recent one and from that retrieving the lot and serial numbers affected by this alert. All this information is processed by AI that later summarizes the causes of the alert and lot/serial numbers.

This web app will allow women to easily check if their contraception is under alert or if it safe to use, while also empowering hard of sight and blind women to be aware of these alerts.  
