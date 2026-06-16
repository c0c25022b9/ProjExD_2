import os
import random
import sys
import time
import pygame as pg


WIDTH, HEIGHT = 1100, 650

DELTA = {
    pg.K_UP:    (0, -5),
    pg.K_DOWN:  (0, +5),
    pg.K_LEFT:  (-5, 0),
    pg.K_RIGHT: (+5, 0),
}


def gameover(screen: pg.Surface) -> None:
    """
    ゲームオーバー画面を表示する関数。
    """
    # 背景を黒に設定
    black_out = pg.Surface((WIDTH, HEIGHT))
    black_out.fill((0, 0, 0))

    # 文字の設定
    fonto = pg.font.Font(None, 120)
    txt = fonto.render("Game Over", True, (255, 255, 255))
    txt_rect = txt.get_rect()
    txt_rect.center = WIDTH // 2, HEIGHT // 2
    
    # こうかとんを文字の左右に配置
    cry_kk_img = pg.transform.rotozoom(pg.image.load("fig/8.png"), 0, 0.9)
    margin = 50
    
    cry_kk_rct1 = cry_kk_img.get_rect()
    cry_kk_rct1.right = txt_rect.left - margin
    cry_kk_rct1.centery = HEIGHT // 2
    
    cry_kk_rct2 = cry_kk_img.get_rect()
    cry_kk_rct2.left = txt_rect.right + margin
    cry_kk_rct2.centery = HEIGHT // 2
    
    # 各Surfaceの貼り付け
    black_out.blit(txt, txt_rect)
    black_out.blit(cry_kk_img, cry_kk_rct1)
    black_out.blit(cry_kk_img, cry_kk_rct2)
    
    # 画面描画と5秒停止
    screen.blit(black_out, [0, 0])
    pg.display.update()
    time.sleep(5)


def check_bound(rct: pg.Rect) -> tuple[bool, bool]:
    """
    画面内・画面外判定関数。
    """
    yoko, tate = True, True
    if rct.left < 0 or WIDTH < rct.right:
        yoko = False
    if rct.top < 0 or HEIGHT < rct.bottom:
        tate = False
    return yoko, tate


def init_bb_imgs() -> tuple[list[pg.Surface], list[int]]:
    """
    10段階の爆弾Surfaceと加速度リストを生成。
    """
    bb_imgs = []
    for r in range(1, 11):
        bb_img = pg.Surface((20 * r, 20 * r))
        bb_img.set_colorkey((0, 0, 0))
        pg.draw.circle(bb_img, (255, 0, 0), (10 * r, 10 * r), 10 * r)
        bb_imgs.append(bb_img)
        
    bb_accs = [a for a in range(1, 11)]
    return bb_imgs, bb_accs


def init_kk_imgs() -> dict[tuple[int, int], pg.Surface]:
    """
    全方向（9パターン）のこうかとん画像辞書を生成。
    """
    kk_img0 = pg.image.load("fig/3.png")
    kk_img1 = pg.transform.flip(kk_img0, True, False)
    
    return {
        (0, 0):   pg.transform.rotozoom(kk_img0, 0, 0.9),
        (+5, 0):  pg.transform.rotozoom(kk_img1, 0, 0.9),
        (+5, -5): pg.transform.rotozoom(kk_img1, 45, 0.9),
        (0, -5):  pg.transform.rotozoom(kk_img1, 90, 0.9),
        (-5, -5): pg.transform.rotozoom(kk_img0, -45, 0.9),
        (-5, 0):  pg.transform.rotozoom(kk_img0, 0, 0.9),
        (-5, +5): pg.transform.rotozoom(kk_img0, 45, 0.9),
        (0, +5):  pg.transform.rotozoom(kk_img1, -90, 0.9),
        (+5, +5): pg.transform.rotozoom(kk_img1, -45, 0.9),
    }


def main():
    pg.display.set_caption("逃げろ！こうかとん")
    screen = pg.display.set_mode((WIDTH, HEIGHT))
    bg_img = pg.image.load("fig/pg_bg.jpg")    
    
    # 各種初期化
    kk_imgs = init_kk_imgs()
    kk_img = kk_imgs[(0, 0)]
    kk_rct = kk_img.get_rect()
    kk_rct.center = 300, 200

    bb_imgs, bb_accs = init_bb_imgs()
    vx, vy = +5, +5
    
    bb_img = bb_imgs[0]
    bb_rct = bb_img.get_rect()
    bb_rct.center = random.randint(0, WIDTH), random.randint(0, HEIGHT)

    clock = pg.time.Clock()
    tmr = 0
    while True:
        for event in pg.event.get():
            if event.type == pg.QUIT: 
                return
                
        screen.blit(bg_img, [0, 0]) 

        # こうかとんの移動処理
        key_lst = pg.key.get_pressed()
        sum_mv = [0, 0]
        for key, mv in DELTA.items():
            if key_lst[key]:
                sum_mv[0] += mv[0]
                sum_mv[1] += mv[1]

        kk_rct.move_ip(sum_mv)
        if check_bound(kk_rct) != (True, True):
            kk_rct.move_ip(-sum_mv[0], -sum_mv[1])  # 画面外なら移動を相殺
            
        # こうかとんの画像変更と描画
        kk_img = kk_imgs[tuple(sum_mv)]
        screen.blit(kk_img, kk_rct)
        
        # 時間経過による爆弾の拡大・加速
        idx = min(tmr // 500, 9)
        avx = vx * bb_accs[idx]
        avy = vy * bb_accs[idx]
        bb_img = bb_imgs[idx]
        
        bb_rct.width = bb_img.get_rect().width
        bb_rct.height = bb_img.get_rect().height

        # 爆弾の移動と跳ね返り
        bb_rct.move_ip(avx, avy)
        yoko, tate = check_bound(bb_rct)
        if not yoko:
            vx *= -1
        if not tate:
            vy *= -1    
        screen.blit(bb_img, bb_rct)

        # 衝突判定
        if kk_rct.colliderect(bb_rct):
            gameover(screen)
            return

        pg.display.update()
        tmr += 1
        clock.tick(50)


if __name__ == "__main__":
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    pg.init()
    main()
    pg.quit()
    sys.exit()