import sys
import time
import os
import requests
from io import BytesIO
from PIL import Image

path, new_dump, delay, x, y, dimx, dimy, fixed = sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5], sys.argv[6], sys.argv[7], sys.argv[8]
images = []
downloaded = []
total = failures = 0
with open('cogs/utils/urls{}.txt'.format(new_dump), 'r') as fp:
    for lines in fp:
        images.append(lines.strip())

os.remove('cogs/utils/urls{}.txt'.format(new_dump))

print('Found {} items. Checking for matches and downloading...'.format(len(images)))
for i, image in enumerate(images):
    sys.stdout.write("\r{}%".format(int((i / len(images)) * 100)))
    sys.stdout.flush()
    if (x != 'None' or dimx != 'None') and (image.endswith(('.jpg', '.jpeg', '.png'))):
        try:
            data = requests.get(image).content
            im = Image.open(BytesIO(data))
            width, height = im.size
            if x != 'None':
                if fixed == 'yes':
                    if width != int(x) or height != int(y):
                        continue
                else:
                    if width < int(x) or height < int(y):
                        continue
            if dimx != 'None':
                if width/int(dimx) != height/int(dimy):
                    continue
        except:
            continue
    image_url = image.split('/')
    image_name = "".join([x if x.isalnum() or x == '.' else "_" for x in image_url[-1]])[-25:]
    if not image_name.endswith(('.jpg', '.jpeg', '.png', '.gif', '.gifv', '.webm')):
        image_name += '.jpg'
    if os.path.exists('{}image_dump/{}/{}'.format(path, new_dump, image_name)):
        duplicate = 1
        dup = True
        while dup:
            if os.path.exists('{}image_dump/{}/{}'.format(path, new_dump, '{}_{}'.format(str(duplicate), image_name))):
                duplicate += 1
            else:
                dup = False
        image_name = '{}_{}'.format(str(duplicate), image_name)
    try:
        image_content = requests.get(image, stream=True).content
        if image_content not in downloaded:
            downloaded.append(image_content)
        else:
            continue
        with open('{}image_dump/{}/{}'.format(path, new_dump, image_name), 'wb') as img:
            img.write(requests.get(image, stream=True).content)

        if 'cdn.discord' in image:
            time.sleep(float(delay))
        total += 1
    except:
        print('\nFailed to save: %s\nContinuing...' % image)
        failures += 1
        try:
            os.remove('{}image_dump/{}/{}'.format(path, new_dump, image_name))
        except:
            pass
stop = time.time()
folder_size = 0
for (path, dirs, files) in os.walk('{}image_dump/{}'.format(path, new_dump)):
    for file in files:
        filename = os.path.join(path, file)
        folder_size += os.path.getsize(filename)
if folder_size/(1024*1024.0) > 1024:
    size = "%0.1f GB" % (folder_size/(1024 * 1024 * 1024.0))
elif folder_size/1024.0 > 1024:
    size = "%0.1f MB" % (folder_size / (1024 * 1024.0))
else:
    size = "%0.1f KB" % (folder_size / 1024.0)
sys.stdout.write('\r100% Done! Downloaded {} items. {}\n'.format(total, size))
sys.stdout.flush()

with open('cogs/utils/finished{}.txt'.format(new_dump), 'w') as fp:
    fp.write('{}\n{}\n{}\n{}'.format(str(stop), str(total), str(failures), size))
