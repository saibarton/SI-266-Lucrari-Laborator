from checker import SITES, build_url, is_https, show_response, check_site, scan_sites, check_headers, retry_check

# Partea 1 - Functii
print("Partea 1 - Functii")
host = SITES[0].replace("https://", "")
print("build_url 1:", build_url(host, "login"))
print("build_url 2:", build_url(host, "/login"))
print("is_https 1:", is_https(SITES[0]))
print("is_https 2:", is_https(SITES[9]))

# Partea 2 - Cereri GET
print("\nPartea 2 - Cereri GET")
print("Site:", SITES[0])
show_response(SITES[0])
print("Site:", SITES[9])
show_response(SITES[9])

# Partea 3 - Verificarea fiecarui site
print("\nPartea 3 - Verificarea site-urilor")
for url in SITES:
    print(url, check_site(url))

# Partea 4 - Scanarea site-urilor
print("\nPartea 4 - Scanarea site-urilor")
scan_sites()

# Partea 5 - Antete de securitate
print("\nPartea 5 - Antete de securitate")
print("Site 1:", check_headers(SITES[10]))
print("Site 2:", check_headers(SITES[11]))
print("Site 3:", check_headers(SITES[9]))

# Partea 6 - Incercari repetate
print("\nPartea 6 - Incercari repetate")
print("Status 200:", retry_check(SITES[3]))
print("Status 404:", retry_check(SITES[6]))
print("Status 500:", retry_check(SITES[7], 2))
print("Site inexistent:", retry_check(SITES[9]))
