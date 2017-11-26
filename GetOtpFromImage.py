import shutil
import cv2, os, sys, pytesseract, re
from PIL import Image
import urllib.request,requests
class GetOtpFromImage():
    def __init__(self,parameters):
        self.image_path = parameters.get("image_url",'')
        self.otp = ''

    def convert_image_with_pil(self):
        self.image = Image.open(self.image_path)
        self.image = self.image.convert('L')
        self.image = self.image.point(lambda x:0 if x<150 else 250,'1')
        self.image.save("new_gray_image.jpg")
    
    def convert_image_with_opencv(self):
        self.image = cv2.imread(self.image_path)
        self.image = cv2.cvtColor(self.image,cv2.COLOR_RGB2GRAY)
        cv2.imwrite("new_gray_image.jpg",self.image)

    def convert_image_with_opencv_gaussian(self):
        self.image = cv2.imread(self.image_path,0)
        self.image = cv2.medianBlur(self.image,5)
        self.image = cv2.adaptiveThreshold(self.image,255,cv2.ADAPTIVE_THRESH_GAUSSIAN_C,cv2.THRESH_BINARY,11,2)
        cv2.imwrite("new_gray_image.jpg",self.image)

    def get_otp_from_text(self,text_from_image):
        if text_from_image:
            otp_pattern = re.compile(r'\d{6}')
            otp_message = re.findall(otp_pattern,text_from_image)
            if otp_message:
                self.otp = otp_message[-1].strip()

    def get_otp(self):
        self.download_img()
        self.convert_image_with_pil()
        text_from_image = pytesseract.image_to_string(Image.open("new_gray_image.jpg"),lang="eng")
        self.get_otp_from_text(text_from_image)
        if not self.otp:
            self.convert_image_with_opencv()
            text_from_image = pytesseract.image_to_string(Image.open("new_gray_image.jpg"),lang="eng")
            self.get_otp_from_text(text_from_image)

        if not self.otp:
            self.convert_image_with_opencv_gaussian()
            text_from_image = pytesseract.image_to_string(Image.open("new_gray_image.jpg"),lang="eng")
            self.get_otp_from_text(text_from_image)


        os.remove("new_gray_image.jpg")
        os.remove("otp_image.jpg")

        return self.otp

    def download_img(self):
        try:
            opener = urllib.request.FancyURLopener({}) 
            opener.version = 'Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.69 Safari/537.36'
            opener.retrieve(self.image_path,"otp_image.jpg")
        except Exception as e:
            print(str(e))
        self.image_path = "otp_image.jpg"

if __name__ == "__main__":
    try:
        image_url = sys.argv[1]
        parameters = {"image_url":image_url
            }
        obj = GetOtpFromImage(parameters)
        otp = obj.get_otp()
        print(otp)
    except Exception as e:
        print(e)
        print("please specify the path of the image as command line argument")
        
