import click
import cv2
from fpdf import FPDF
from natsort import natsorted
import ntpath
import os

def video_to_imgs(filename, diff_thresh):
	video = cv2.VideoCapture(filename)
	try:
		# creating a folder named data
		if not os.path.exists('data'):
			os.makedirs('data')
	# if not created then raise error
	except OSError:
		print ('Error: Creating directory of data')
	# frame
	current_frame = 0
	last_frame = []
	while(True):
		# reading from frame
		ret, frame = video.read()
		if ret:
			# if video is still left continue creating images
			name = './data/frame' + str(current_frame) + '.jpg'
			g_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
			if len(last_frame):
				g_last_frame = cv2.cvtColor(last_frame, cv2.COLOR_BGR2GRAY)
				if cv2.absdiff(g_frame, g_last_frame).mean() > diff_thresh:
					# writing the extracted images
					print ('Creating...' + name)
					cv2.imwrite(name, frame)
			else:
				print ('Creating...' + name)
				cv2.imwrite(name, frame)
			# increasing counter so that it will
			# show how many frames are created
			current_frame += 1
			last_frame = frame.copy()
		else:
			break
	# Release all space and windows once done
	video.release()
	cv2.destroyAllWindows()
	return last_frame

def create_pdf(orientation, form, output):
	pdf = FPDF(format=form, orientation=orientation)
	for im_name in natsorted(os.listdir("data")):
		pdf.add_page()
		if orientation == "L":
			pdf.image(os.path.join("data", im_name), 0, 0, 297, 210)
		else:
			pdf.image(os.path.join("data", im_name), 0, 0, 210, 297)
	pdf.output(output)

@click.command()
@click.argument('filename', type=click.Path(exists=True))
@click.option('--output', '-o', default='', help='Output filename')
@click.option('--diff_thresh', '-d', default=5, help='Images Diff Threshold')
def main(filename, output, diff_thresh):
	last_frame = video_to_imgs(filename, diff_thresh)
	# creating pdf
	if len(last_frame):
		output = ntpath.basename(filename)[:-4] + ".pdf" if len(output) == 0 else output
		orientation = 'L' if last_frame.shape[0] < last_frame.shape[1] else 'P'
		form = "A4"
		create_pdf(orientation, form, output)
		print("Successfully Created %s file" % output)
if __name__ == '__main__':
	main()