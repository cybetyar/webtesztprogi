#!/usr/bin/env python2
import mechanize
import socket
from urlparse import urlparse
from re import search, sub
import cookielib
import requests
import os
from urllib import urlencode
from plugins.DNSDumpsterAPI import DNSDumpsterAPI
import whois
import json

params = []
# Browser
br = mechanize.Browser()

# Just some colors and shit
white = '\033[1;97m'
green = '\033[1;32m'
red = '\033[1;31m'
yellow = '\033[1;33m'
end = '\033[1;m'
info = '\033[1;33m[!]\033[1;m'
que =  '\033[1;34m[?]\033[1;m'
bad = '\033[1;31m[-]\033[1;m'
good = '\033[1;32m[+]\033[1;m'
run = '\033[1;97m[~]\033[1;m'

# Cookie Jar
cj = cookielib.LWPCookieJar()
br.set_cookiejar(cj)

# Browser options
br.set_handle_equiv(True)
br.set_handle_redirect(True)
br.set_handle_referer(True)
br.set_handle_robots(False)

# Follows refresh 0 but not hangs on refresh > 0
br.set_handle_refresh(mechanize._http.HTTPRefreshProcessor(), max_time=1)
br.addheaders = [
    ('User-agent', 'Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.9.0.1) Gecko/2008071615 Fedora/3.0.1-1.fc9 Firefox/3.0.1')]


 '''\033[1;31m
CYBEtyaR - A MAGYAR HACKER KOZOSSEG
\\A szamitogep az ember logikai tovabbfejlesztese: intelligencia erkolcs nelkul//
\033[1;m'''
target_input = raw_input('\033[1;34m[?]\033[1;m Ki a celpont: example( http://domain.com ) \n')
parsed_uri = urlparse(target_input)

if parsed_uri.scheme == '':
    domain = parsed_uri.path
else:
    domain = parsed_uri.netloc

target = '{}//{}'.format(parsed_uri.scheme, domain) #detect HTTP or HTTPs By UrlParse

def sqli(url):
    print '%s Az SQLMAP Api-jat hasznaljuk scanneleshez. Ne parazz, ez nem mulik az internetkapcsolatodon. Kb 2-3 perc :)' % run
    br.open('https://suip.biz/?act=sqlmap')
    br.select_form(nr=0)
    br.form['url'] = url
    req = br.submit()
    result = req.read()
    match = search(r"---(?s).*---", result)
    if match:
        print '%s Egy vagy tobb sebezheto parametert talaltunk' % good
        option = raw_input(
            '%s Akarod latni a teljes eredmenyt? [Y/n] ' % que).lower()
        if option == 'n':
            pass
        else:
            print '\033[1;31m-\033[1;m' * 40
            print match.group().split('---')[1][:-3]
            print '\033[1;31m-\033[1;m' * 40
    else:
        print '%s Nem sebezheto :( ' % bad


def cms(domain):
    try:
        result = br.open('https://whatcms.org/?s=' + domain).read()
        detect = search(r'class="nowrap" title="[^<]*">', result)
        WordPress = False
        try:
            r = br.open('//' + domain + '/robots.txt').read()
            if "wp-admin" in str(r):
                WordPress = True
        except:
            pass
        if detect:
            print '%s CMS Megtalalva : %s' % (info, detect.group().split('class="nowrap" title="')[1][:-2])
            detect = detect.group().split('">')[1][:-27]
            if 'WordPress' in detect:
                option = raw_input(
                    '%s Would you like to use WPScan? [Y/n] ' % que).lower()
                if option == 'n':
                    pass
                else:
                    os.system('wpscan --random-agent --url %s' % domain)
        elif WordPress:
            print '%s CMS Megtalalva : WordPress' % info
            option = raw_input(
                '%s Szeretned hasznalni a WPScan-t? [Y/n] ' % que).lower()
            if option == 'n':
                pass
            else:
                os.system('wpscan --random-agent --url %s' % domain)
        else:
            print '%s %s ugy tunik a celpont nem hasznal CMS-t' % (info, domain)
    except:
        pass

def honeypot(ip_addr):
    result = {"0.0": 0, "0.1": 10, "0.2": 20, "0.3": 30, "0.4": 40, "0.5": 50, "0.6": 60, "0.7": 70, "0.8": 80, "0.9": 90, "1.0": 10}
    honey = 'https://api.shodan.io/labs/honeyscore/%s?key=C23OXE0bVMrul2YeqcL7zxb6jZ4pj2by' % ip_addr
    try:
        phoney = br.open(honey).read()
        if float(phoney) >= 0.0 and float(phoney) <= 0.4:
            what = good
        else:
            what = bad
        print '{} Honeypot Eredmeny: {}%'.format(what, result[phoney])
    except KeyError:
        print '\033[1;31m[-]\033[1;m Honeypot-ra vedett'

def whoisIt(url):
    who = ""
    print '{} Whois adatok megszerzese {}'.format(run,url)
    try:
        who = str(whois.whois(url)).decode()
    except Exception:
        pass
    test = who.lower()
    if "whoisguard" in test or "protection" in test or "protected" in test:
        print '{} Whois Vedelem Bekapcsolva{}'.format(bad, end)
    else:
        print '{} Whois informaciot talaltunk{}'.format(good, end)
        try:
            data = json.loads(who)
            for key in data.keys():
                print "{} :".format(key.replace("_", " ").title()),
                if type(data[key]) == list:
                    print ", ".join(data[key])
                else:
                    print "{}".format(data[key])
        except ValueError:
            print '{} Nem tudtuk megcsinalni :( keresd fel: https://who.is/whois/{} {}'.format(bad, url, end) 
    pass

def nmap(ip_addr):
    port = 'http://api.hackertarget.com/nmap/?q=' + ip_addr
    result = br.open(port).read()
    result = sub(r'Starting[^<]*\)\.', '', result)
    result = sub(r'Service[^<]*seconds', '', result)
    result = os.linesep.join([s for s in result.splitlines() if s])
    print result

def bypass(domain):
    post = urlencode({'cfS': domain})
    result = br.open(
        'http://www.crimeflare.info/cgi-bin/cfsearch.cgi ', post).read()

    match = search(r' \b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b', result)
    if match:
        bypass.ip_addr = match.group().split(' ')[1][:-1]
        print '%s Valos IP cim : %s' % (good, bypass.ip_addr)

def dnsdump(domain):
    res = DNSDumpsterAPI(False).search(domain)
    if not res:
        print '\n%s DNS Rekordok' % bad
        return

    print '\n%s DNS Rekordok' % good

    for entry in res.get('dns_records', {}).get('dns', []):
        print '{domain} ({ip}) {as} {provider} {country}'.format(**entry)

    for entry in res.get('dns_records', {}).get('mx', []):
        print '\n%s MX Rekordok' % good
        print '{domain} ({ip}) {as} {provider} {country}'.format(**entry)
    print '\n\033[1;32m[+]\033[1;m Host Rekordok (A)'

    for entry in res.get('dns_records', {}).get('host', []):
        if entry.get('reverse_dns', None):
            print '{domain} ({reverse_dns}) ({ip}) {as} {provider} {country}'.format(**entry)
        else:
            print '{domain} ({ip}) {as} {provider} {country}'.format(**entry)
    print '\n%s TXT Rekordok' % good

    for entry in res.get('dns_records', {}).get('txt', []):
        print entry
    print '\n%s DNS Terkep: https://dnsdumpster.com/static/map/%s.png\n' % (good, domain.strip('www.'))


def fingerprint(ip_addr):
    try:
        result = br.open('https://www.censys.io/ipv4/%s/raw' % ip_addr).read()
        match = search(r'&#34;os_description&#34;: &#34;[^<]*&#34;', result)
        if match:
            print '%s Operacios Rendszer : %s' % (good, match.group().split('n&#34;: &#34;')[1][:-5])
    except:
        pass


ip_addr = socket.gethostbyname(domain)
print '%s IP Cim : %s' % (info, ip_addr)
try:
    r = requests.get(target)
    header = r.headers['Server']
    if 'cloudflare' in header:
        print '%s Cloudflare Rendszert Talaltunk' % bad
        bypass(domain)
        try:
            ip_addr = bypass.ip_addr
        except:
            pass
    else:
        print '%s Szerver: %s' % (info, header)
    try:
        print '%s Uzemelteto: %s' % (info, r.headers['X-Powered-By'])
    except:
        pass
    try:
        r.headers['X-Frame-Options']
    except:
        print '%s Clickjacking Ellen Nem Vedett.' % good
except:
    pass
fingerprint(ip_addr)
cms(domain)
try:
    honeypot(ip_addr)
except:
    pass
print "{}----------------------------------------{}".format(red, end)
whoisIt(domain)
try:
    r = br.open(target + '/robots.txt').read()
    print '\033[1;31m-\033[1;m' * 40
    print '%s Robots.txt Elerheto\n' % good, r
except:
    pass
print '\033[1;31m-\033[1;m' * 40
nmap(ip_addr)
print '\033[1;31m-\033[1;m' * 40
dnsdump(domain)
os.system('cd plugins && python theHarvester.py -d %s -b all' % domain)
try:
    br.open(target)
    print '%s Nezzuk meg, hogy van-e visszafejtheto URL' % run
    for link in br.links():
        if 'http' in link.url or '=' not in link.url:
            pass
        else:
            url = target + '/' + link.url
            params.append(url)
    if len(params) == 0:
        print '%s Nem talaltunk URL-t' % bad
        quit()
    print '%s Talalat %i URL' % (good, len(params))
    for url in params:
        print url
        sqli(url)
        url = url.replace('=', '<svg/onload=alert()>')
        r = br.open(url).read()
        if '<svg/onload=alert()>' in r:
            print '%s XSS Sebezhetoseget Talaltunk' % good
        break
    print '%s Ime:' % good
    for url in params:
        print url
except:
    pass