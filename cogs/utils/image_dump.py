import sys
import time
import os
import requests
import hashlib
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
finished_status = images
for i, image in enumerate(images):
    if image[0] == '-':
        continue
    if image[0] == '+' and ' ' in image:
        image_hash = image[1:].split(' ', 1)[0]
        downloaded.append(image_hash)
        total += 1
        continue
    finished_status[i] = '-' + finished_status[i]
    sys.stdout.write('\rStatus: {}% | Downloaded: {} | Checked: {}/{}'.format(int((i / len(images)) * 100), total, i, len(images)))
    sys.stdout.flush()
    if os.path.exists('pause.txt'):
        with open('cogs/utils/urls{}.txt'.format(new_dump), 'w') as fp:
            for links in finished_status:
                fp.write(links + '\n')
        with open('cogs/utils/paused{}.txt'.format(new_dump), 'w') as fp:
            fp.write('{}%'.format(int((i / len(images)) * 100)))
            fp.write('\n{}\n{}\n{}\n{}\n{}\n{}\n{}\n{}'.format(path, new_dump, delay, x, y, dimx, dimy, fixed))
        os._exit(0)

    failed = False
    for i in range(3):
        try:
            response = requests.get(image, stream=True)
            data = response.content
            break
        except:
            time.sleep(2)
            if i == 2:
                failed = True
                sys.stdout.write('\rFailed to retrieve: %s                       ' % image)
                sys.stdout.flush()
                print('\nContinuing...')
                failures += 1
            continue
    if failed:
        continue

    if (x != 'None' or dimx != 'None') and (image.endswith(('.jpg', '.jpeg', '.png'))):
        try:
            im = Image.open(BytesIO(data))
            width, height = im.size
            if x != 'None':
                if fixed == 'yes':
                    if width != int(x) or height != int(y):
                        continue
                elif fixed == 'more':
                    if width < int(x) or height < int(y):
                        continue
                else:
                    if width > int(x) or height > int(y):
                        continue
            if dimx != 'None':
                if width/int(dimx) != height/int(dimy):
                    continue
        except:
            continue

    image_hash = hashlib.md5(data).hexdigest()
    if image_hash not in downloaded:
        downloaded.append(image_hash)
    else:
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

        with open('{}image_dump/{}/{}'.format(path, new_dump, image_name), 'wb') as img:

            for block in response.iter_content(1024):
                if not block:
                    break

                img.write(block)

        if 'cdn.discord' in image:
            time.sleep(float(delay))
        total += 1
        finished_status[i] = '+{} {}'.format(image_hash, finished_status[i])
    except:
        sys.stdout.write('\rUnable to save image to folder: %s                       ' % image)
        sys.stdout.flush()
        print('\nContinuing...')
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
sys.stdout.write('\r100% Done! Downloaded {} items. {}                         \n'.format(total, size))
sys.stdout.flush()

with open('cogs/utils/finished{}.txt'.format(new_dump), 'w') as fp:
    fp.write('{}\n{}\n{}\n{}'.format(str(stop), str(total), str(failures), size))
