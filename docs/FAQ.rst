FAQ
####################

Why netscud?
************

Very few changes from netdev (the first serious network device async python library created by Sergey Yakovlev) recently pushes me to create netscud. It cannot challenge netdev - I am far from an expert in developpement - but it has nice features I needed. Other people may need them. It is above all a personal challenge.

netdev github site can be found at: https://github.com/selfuryon

A short description of netscud?
*******************************

netscud is like netdev (Ayns SSH) + napalm (API) + nornir (Inventory + concurrency function) in one package.

When is it interesting to use non-blocking technique like async?
****************************************************************

It is interesting when there are commands send concurrently on more than 1 device and when using threads or processes is not wanted. In that configuration speed is fast and there is less troubles than managing race conditions on resources with locks.

Why the name netscud?
*********************

- netscud purpose is to be fast like a rocket.
- Also it is inspired by netdev async library coming from Russia; so it is recognition of the work done by the author of netdev.
- And finally I needed a name not already used by a python library.
