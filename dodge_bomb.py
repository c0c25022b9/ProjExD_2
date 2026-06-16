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
    画面を完全にブラックアウトし、中央に大きな「Game Over」の文字、そのすぐ左右に泣いているこうかとんを配置して5秒間表示する。
    引数 screen: 描画対象の画面Surface
    """
    # 暗転する画面（アップロード画像に合わせて不透明の完全な黒に設定）
    black_out = pg.Surface((WIDTH, HEIGHT))
    black_out.fill((0, 0, 0))

    # "Game Over"の設定（第1回資料P.53の変数名を採用し、サイズを画像同様の120に拡大）
    fonto = pg.font.Font(None, 120)
    txt = fonto.render("Game Over", True, (255, 255, 255))
    txt_rect = txt.get_rect()
    txt_rect.center = WIDTH // 2, HEIGHT // 2
    
    # 泣くこうかとん（第1回資料P.55のRect相対位置指定を使い、文字のすぐ左右に精密配置）
    cry_kk_img = pg.transform.rotozoom(pg.image.load("fig/8.png"), 0, 0.9)
    margin = 50  # 文字とこうかとんの間の余白
    
    cry_kk_rct1 = cry_kk_img.get_rect()
    cry_kk_rct1.right = txt_rect.left - margin
    cry_kk_rct1.centery = HEIGHT // 2
    
    cry_kk_rct2 = cry_kk_img.get_rect()
    cry_kk_rct2.left = txt_rect.right + margin
    cry_kk_rct2.centery = HEIGHT // 2
    
    # 暗い画面にテキストと画像を貼り付ける
    black_out.blit(txt, txt_rect)
    black_out.blit(cry_kk_img, cry_kk_rct1)
    black_out.blit(cry_kk_img, cry_kk_rct2)
    
    # 通常画面への反映
    screen.blit(black_out, [0, 0])
    pg.display.update()
    time.sleep(5)


def check_bound(rct: pg.Rect) -> tuple[bool, bool]:
    """
    引数：こうかとんRect or 爆弾Rect
    戻り値：判定結果タプル （横方向判定結果、縦方向判定結果）
    画面内ならTrue, 画面外ならFalse
    """
    yoko, tate = True, True
    if rct.left < 0 or WIDTH < rct.right:
        yoko = False
    if rct.top < 0 or HEIGHT < rct.bottom:
        tate = False
    return yoko, tate


def init_bb_imgs() -> tuple[list[pg.Surface], list[int]]:
    """
    追加機能2: サイズと加速度が異なる爆弾のリストを生成する関数
    戻り値: 10段階の爆弾Surfaceのリストと、10段階の加速度のリストのタプル
    """
    bb_imgs = []
    # 10段階の大きさを変えた爆弾Surfaceを準備
    for r in range(1, 11):
        bb_img = pg.Surface((20 * r, 20 * r))
        bb_img.set_colorkey((0, 0, 0))  # 黒い背景を透明化
        pg.draw.circle(bb_img, (255, 0, 0), (10 * r, 10 * r), 10 * r)
        bb_imgs.append(bb_img)
        
    # 10段階の加速度のリストを準備
    bb_accs = [a for a in range(1, 11)]
    return bb_imgs, bb_accs


def main():
    pg.display.set_caption("逃げろ！こうかとん")
    screen = pg.display.set_mode((WIDTH, HEIGHT))
    bg_img = pg.image.load("fig/pg_bg.jpg")    
    kk_img = pg.transform.rotozoom(pg.image.load("fig/3.png"), 0, 0.9)
    kk_rct = kk_img.get_rect()
    kk_rct.center = 300, 200

    # 追加機能2: while文の前で関数を呼び出して2つのリストを得る
    bb_imgs, bb_accs = init_bb_imgs()
    vx, vy = +5, +5
    
    # 最初の爆弾のRectを設定（インデックス0の初期サイズ）
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

        # こうかとんの移動
        key_lst = pg.key.get_pressed()
        sum_mv = [0, 0]
        for key, mv in DELTA.items():
            if key_lst[key]:
                sum_mv[0] += mv[0]   # 横方向の移動
                sum_mv[1] += mv[1]   # 縦方向の移動

        kk_rct.move_ip(sum_mv)
        if check_bound(kk_rct) != (True, True):
            kk_rct.move_ip(-sum_mv[0], -sum_mv[1])   # 動作のキャンセル
            
        screen.blit(kk_img, kk_rct)
        
        # 追加機能2: while文の中でtmrの値に応じて、リストから適切な要素を選択する
        idx = min(tmr // 500, 9)  # 500フレームごとに段階が上がる（最大インデックスは9）
        avx = vx * bb_accs[idx]
        avy = vy * bb_accs[idx]
        bb_img = bb_imgs[idx]
        
        # 追加機能2: Surfaceの大きさが変わった場合は、Rectのwidthとheight属性を更新する
        bb_rct.width = bb_img.get_rect().width
        bb_rct.height = bb_img.get_rect().height

        # 拡大・加速した移動量で爆弾を移動
        bb_rct.move_ip(avx, avy)
        
        yoko, tate = check_bound(bb_rct)
        if not yoko:   # 横方向のはみ出し
            vx *= -1
        if not tate:   # 縦方向のはみ出し
            vy *= -1    
        screen.blit(bb_img, bb_rct)

        # 衝突したらgameover関数を呼び出す
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