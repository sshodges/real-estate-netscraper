import urllib2, json, time
import sqlite3 as lite

con = lite.connect('realestate.db')
c = con.cursor()
c.execute('''CREATE TABLE IF NOT EXISTS properties
    (id integer PRIMARY KEY, listingId integer, daySold integer, monthSold integer, yearSold integer, address text, suburb text, postCode text, price real, landSize real, propertyType, bedrooms real, bathrooms real, parkingSpaces real)''')

linkHome = ("https://www.realestate.com.au/sold/")

inputPostCode = raw_input("What post code would you like to download?")
link = '/sold/in-' + inputPostCode + '/list-1?includeSurrounding=false&activeSort=solddate&source=refinement'
for i in range(1, 100):

    response = urllib2.urlopen("https://www.realestate.com.au"+link)

    page_source = response.read()

    results = page_source.split('"results":')[1].split("</script>")[0].split('"channel"')

    object = '{"results": ['
    for page in results[1:-2]:
        if page.startswith(':"sold"'):
            object += '{"channel"' + page[:-2] + ','
    object = object[:-2] + '}]}'

    data = json.loads(object)

    house1 = data['results']
    for house in house1:
        try:
            listingId = house['listingId']
            address = house['address']['streetAddress']
            suburb = house['address']['suburb']
            postCode = house['address']['postCode']
            price = house['price']['display']
            price = price.lower()
            date = house['dateSold']['value']
            daySold = date.split('-')[2]
            monthSold = date.split('-')[1]
            yearSold = date.split('-')[0]

            if price == 'contact agent':
                price = ''
            else:
                price = price.replace('$','')
                price = price.replace(',','')
            try:
                landSize = house['landSize']['value']
            except:
                landSize = ''
            propertyType = house['propertyType']
            bedrooms = house['features']['general']['bedrooms']
            bathrooms = house['features']['general']['bathrooms']
            parkingSpaces = house['features']['general']['parkingSpaces']
            propertyFind = [(listingId, daySold, monthSold, yearSold, address, suburb, postCode, price, landSize, propertyType, bedrooms, bathrooms, parkingSpaces)]

            c.execute('SELECT * FROM properties WHERE listingId=?', (listingId,))
            if c.fetchone() == None:
                c.executemany('INSERT INTO properties VALUES (NULL,?,?,?,?,?,?,?,?,?,?,?,?,?)', propertyFind)
                con.commit()
            else:
                print 'Item exisits'
        except:
            print link


    try:
        link = page_source.split('Go to Next Page')[1].split('href="')[1].split('"')[0]
    except:
        print "https://www.realestate.com.au" + link

    time.sleep(3)
    print i

print ("https://www.realestate.com.au"+link)
