import os
import cv2
import numpy as np
from blind_watermark import WaterMark, att
from blind_watermark.recover import estimate_crop_parameters, recover_crop

CONFIG = {
    'input_image': 'input/input.png',
    'output_dir': 'output',
    'embedded_image_name': 'embedded.png',
    'watermark_text': 'DingHaa',
    'password_img': 1,
    'password_wm': 1,
    'attacks': {
        'screenshot_known': {'loc_r': ((0.1, 0.1), (0.5, 0.5)), 'scale': 0.7},
        'screenshot_unknown': {'loc_r': ((0.1, 0.1), (0.7, 0.6)), 'scale': 0.7},
        'rotation': {'angle': 60},
        'shelter': {'ratio': 0.1, 'n': 60},
        'resize': {'out_shape': (400, 300)},
        'brightness': {'ratio': 0.9},
    }
}

class WatermarkAttackSuite:
    def __init__(self, config):
        self.config = config
        self.output_dir = self.config['output_dir']
        self.embedded_file = os.path.join(self.output_dir, self.config['embedded_image_name'])
        self.wm_len = 0
        self.original_image_shape = None
        self.embedder = WaterMark(password_img=self.config['password_img'], password_wm=self.config['password_wm'])
        self.extractor = WaterMark(password_img=self.config['password_img'], password_wm=self.config['password_wm'])

    def _verify_watermark(self, attack_name, file_to_extract):
        print(f"--- Verifying: {attack_name} ---")
        if not os.path.exists(file_to_extract):
            print(f"❌ FAILURE: File not found at '{file_to_extract}'. Cannot verify.")
            return
        extracted_wm = self.extractor.extract(file_to_extract, wm_shape=self.wm_len, mode='str')
        print(f"Extraction result: '{extracted_wm}'")
        expected_wm = self.config['watermark_text']
        if expected_wm == extracted_wm:
            print(f"✅ SUCCESS: Watermark correctly extracted for '{attack_name}'.\n")
        else:
            print(f"❌ FAILURE: Watermark mismatch for '{attack_name}'. Expected '{expected_wm}'.\n")
        assert expected_wm == extracted_wm

    def _prepare_environment(self):
        os.chdir(os.path.dirname(os.path.abspath(__file__)))
        os.makedirs(self.output_dir, exist_ok=True)
        print("--- Embedding Watermark ---")
        self.embedder.read_img(self.config['input_image'])
        self.embedder.read_wm(self.config['watermark_text'], mode='str')
        self.embedder.embed(self.embedded_file)
        self.wm_len = len(self.embedder.wm_bit)
        self.original_image_shape = cv2.imread(self.config['input_image']).shape[:2]
        print(f"Embedded '{self.config['watermark_text']}' into '{self.embedded_file}' (bit length: {self.wm_len}).\n")

    def test_no_attack(self):
        self._verify_watermark("No Attack", self.embedded_file)

    def test_screenshot_known_params(self):
        params = self.config['attacks']['screenshot_known']
        h, w = self.original_image_shape
        loc_r, scale = params['loc_r'], params['scale']
        x1, y1, x2, y2 = int(w * loc_r[0][0]), int(h * loc_r[0][1]), int(w * loc_r[1][0]), int(h * loc_r[1][1])
        attacked_file = os.path.join(self.output_dir, 'attack_screenshot_known.png')
        recovered_file = os.path.join(self.output_dir, 'attack_screenshot_known_recovered.png')
        att.cut_att3(input_filename=self.embedded_file, output_file_name=attacked_file, loc=(x1, y1, x2, y2), scale=scale)
        
        if not os.path.exists(attacked_file):
            print(f"❌ FAILURE: Attack function failed to create '{attacked_file}'.")
            return

        recover_crop(template_file=attacked_file, output_file_name=recovered_file, loc=(x1, y1, x2, y2),
                     image_o_shape=self.original_image_shape)
        self._verify_watermark("Screenshot Attack (Known Params)", recovered_file)

    def test_screenshot_unknown_params(self):
        params = self.config['attacks']['screenshot_unknown']
        h, w, _ = cv2.imread(self.embedded_file).shape
        loc_r, scale = params['loc_r'], params['scale']
        x1_r, y1_r, x2_r, y2_r = int(w * loc_r[0][0]), int(h * loc_r[0][1]), int(w * loc_r[1][0]), int(h * loc_r[1][1])
        attacked_file = os.path.join(self.output_dir, 'attack_screenshot_unknown.png')
        recovered_file = os.path.join(self.output_dir, 'attack_screenshot_unknown_recovered.png')
        
        att.cut_att3(input_filename=self.embedded_file, output_file_name=attacked_file, loc=(x1_r, y1_r, x2_r, y2_r), scale=scale)
        
        if not os.path.exists(attacked_file):
            print(f"❌ FAILURE: Attack function failed to create '{attacked_file}'.")
            return

        (x1, y1, x2, y2), img_o_shape, score, scale_infer = estimate_crop_parameters(
            original_file=self.embedded_file, template_file=attacked_file, scale=(0.5, 2), search_num=200)
        print(f"Estimated params: x1={x1}, y1={y1}, x2={x2}, y2={y2}, scale={scale_infer:.2f} (score={score:.2f})")
        
        recover_crop(template_file=attacked_file, output_file_name=recovered_file, loc=(x1, y1, x2, y2), image_o_shape=img_o_shape)
        self._verify_watermark("Screenshot Attack (Unknown Params)", recovered_file)

    def test_rotation_attack(self):
        angle = self.config['attacks']['rotation']['angle']
        attacked_file = os.path.join(self.output_dir, 'attack_rotation.png')
        recovered_file = os.path.join(self.output_dir, 'attack_rotation_recovered.png')
        
        att.rot_att(input_filename=self.embedded_file, output_file_name=attacked_file, angle=angle)
        
        if not os.path.exists(attacked_file):
            print(f"❌ FAILURE: Attack function failed to create '{attacked_file}'.")
            return

        att.rot_att(input_filename=attacked_file, output_file_name=recovered_file, angle=-angle)
        self._verify_watermark(f"Rotation Attack (Angle={angle})", recovered_file)

    def test_shelter_attack(self):
        params = self.config['attacks']['shelter']
        attacked_file = os.path.join(self.output_dir, 'attack_shelter.png')
        att.shelter_att(input_filename=self.embedded_file, output_file_name=attacked_file, ratio=params['ratio'], n=params['n'])
        self._verify_watermark(f"Shelter Attack (n={params['n']})", attacked_file)

    def test_resize_attack(self):
        out_shape = self.config['attacks']['resize']['out_shape']
        attacked_file = os.path.join(self.output_dir, 'attack_resize.png')
        recovered_file = os.path.join(self.output_dir, 'attack_resize_recovered.png')
        
        att.resize_att(input_filename=self.embedded_file, output_file_name=attacked_file, out_shape=out_shape)
        
        if not os.path.exists(attacked_file):
            print(f"❌ FAILURE: Attack function failed to create '{attacked_file}'.")
            return

        att.resize_att(input_filename=attacked_file, output_file_name=recovered_file, out_shape=self.original_image_shape[::-1])
        self._verify_watermark("Resize Attack", recovered_file)

    def test_brightness_attack(self):
        ratio = self.config['attacks']['brightness']['ratio']
        attacked_file = os.path.join(self.output_dir, 'attack_brightness.png')
        recovered_file = os.path.join(self.output_dir, 'attack_brightness_recovered.png')
        
        att.bright_att(input_filename=self.embedded_file, output_file_name=attacked_file, ratio=ratio)
        
        if not os.path.exists(attacked_file):
            print(f"❌ FAILURE: Attack function failed to create '{attacked_file}'.")
            return

        att.bright_att(input_filename=attacked_file, output_file_name=recovered_file, ratio=1/ratio)
        self._verify_watermark("Brightness Attack", recovered_file)

    def run(self):
        self._prepare_environment()
        test_methods = [getattr(self, method) for method in dir(self) if method.startswith('test_') and callable(getattr(self, method))]
        for test in test_methods:
            try:
                test()
            except Exception as e:
                print(f"💥 An exception occurred during '{test.__name__}': {e}\n")

def main():
    suite = WatermarkAttackSuite(config=CONFIG)
    suite.run()

if __name__ == '__main__':
    main()