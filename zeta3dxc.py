from rcon.source import Client
import numpy as np
import time

class RiemannZetaCriticalLine:
    def __init__(self, host='localhost', port=25575, password='password'):
        self.rcon = Client(host, port)
        self.rcon.__enter__()
        try:
            self.rcon.login(password)
        except Exception as e:
            self.rcon.__exit__(None, None, None)
            raise

        self.center_x = 0
        self.center_y = 70
        self.center_z = 0

        self.clear_area()

    def close(self):
        if self.rcon:
            self.rcon.__exit__(None, None, None)

    def execute(self, command):
        try:
            response = self.rcon.run(command)
            if isinstance(response, bytes):
                response = response.decode('utf-8')
            return response
        except Exception as e:
            return None

    def clear_area(self):
        size = 150
        self.execute(f"fill {self.center_x-size} {self.center_y-20} {self.center_z-size} "
                     f"{self.center_x+size} {self.center_y+80} {self.center_z+size} air")

    def approx_zeta_via_eta(self, s, N=2000):
        eta = 0.0 + 0.0j
        for n in range(1, N+1):
            sign = 1 if n % 2 == 1 else -1
            eta += sign * np.exp(-s * np.log(n))
        denom = 1 - 2**(1 - s)
        if abs(denom) < 1e-12:
            return 1e10 + 0j
        return eta / denom

    def draw_critical_line_3d(self,
                              t_min=-50, t_max=50,
                              num_points=1200,
                              N=2000,
                              t_scale=2.0,
                              re_im_scale=10.0):
        sigma = 0.5
        t_values = np.linspace(t_min, t_max, num_points)
        points = []
        for t in t_values:
            s = complex(sigma, t)
            zeta_val = self.approx_zeta_via_eta(s, N)
            points.append((t, zeta_val))

        color_map = [
            'red_wool', 'orange_wool', 'yellow_wool', 'lime_wool',
            'green_wool', 'cyan_wool', 'light_blue_wool', 'blue_wool',
            'purple_wool', 'magenta_wool', 'pink_wool'
        ]

        zero_count = 0
        for i, (t, zeta_val) in enumerate(points):
            re = zeta_val.real
            im = zeta_val.imag
            mag = abs(zeta_val)

            x = self.center_x + int((t - t_min) * t_scale)
            y = self.center_y + int(re * re_im_scale)
            z = self.center_z + int(im * re_im_scale)

            if mag < 0.05:
                block = "glowstone"
                zero_count += 1
            else:
                t_norm = (t - t_min) / (t_max - t_min)
                color_index = int(t_norm * len(color_map))
                color_index = max(0, min(color_index, len(color_map)-1))
                block = color_map[color_index]

            self.execute(f"setblock {x} {y} {z} {block}")

            if i % 200 == 0:
                time.sleep(0.05)

if __name__ == "__main__":
    HOST = "localhost"
    PORT = 25575
    PASSWORD = "MySecret123"

    viz = RiemannZetaCriticalLine(HOST, PORT, PASSWORD)

    viz.draw_critical_line_3d(
        t_min=-50,
        t_max=50,
        num_points=1500,
        N=2000,
        t_scale=2.5,
        re_im_scale=12.0
    )

    viz.close()