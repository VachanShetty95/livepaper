# Maintainer: Vachan Shetty
pkgname=livepaper
pkgver=1.0.0
pkgrel=1
pkgdesc="A polished video wallpaper manager for KDE Plasma 6"
arch=('any')
url="https://github.com/VachanShetty95/livepaper"
license=('MIT')
depends=(
    'python>=3.11'
    'python-pyqt6'
    'python-pydantic'
    'plasma6-wallpapers-smart-video-wallpaper-reborn'
    'qt6-multimedia'
    'qt6-multimedia-ffmpeg'
    'ffmpeg'
)
makedepends=(
    'python-build'
    'python-installer'
    'python-wheel'
    'python-hatchling'
)
source=("${pkgname}-${pkgver}.tar.gz::${url}/archive/v${pkgver}.tar.gz")
sha256sums=('SKIP')

build() {
    cd "${pkgname}-${pkgver}"
    python -m build --wheel --no-isolation
}

package() {
    cd "${pkgname}-${pkgver}"
    python -m installer --destdir="${pkgdir}" dist/*.whl

    install -Dm644 resources/livepaper.desktop \
        "${pkgdir}/usr/share/applications/livepaper.desktop"

    install -Dm644 LICENSE \
        "${pkgdir}/usr/share/licenses/${pkgname}/LICENSE"
}
