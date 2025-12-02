"""
使用 uv 创建环境并打包成 exe 的构建脚本
"""
import os
import sys
import subprocess
import shutil
from pathlib import Path

def check_uv_installed():
    """检查 uv 是否已安装"""
    try:
        result = subprocess.run(['uv', '--version'], 
                              capture_output=True, 
                              text=True, 
                              check=True)
        print(f"[SUCCESS] uv 已安装: {result.stdout.strip()}")
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("[ERROR] uv 未安装")
        print("[INFO] 正在安装 uv...")
        try:
            subprocess.run([sys.executable, '-m', 'pip', 'install', 'uv'], check=True)
            print("[SUCCESS] uv 安装成功")
            return True
        except subprocess.CalledProcessError:
            print("[ERROR] 无法安装 uv，请手动安装: pip install uv")
            return False

def create_venv_with_uv():
    """使用 uv 创建虚拟环境"""
    venv_path = Path('.venv')
    if venv_path.exists():
        print("[INFO] 虚拟环境已存在，跳过创建")
        return True
    
    print("[INFO] 正在使用 uv 创建虚拟环境...")
    try:
        subprocess.run(['uv', 'venv'], check=True)
        print("[SUCCESS] 虚拟环境创建成功")
        return True
    except subprocess.CalledProcessError as e:
        print(f"[ERROR] 创建虚拟环境失败: {e}")
        return False

def install_dependencies():
    """使用 uv 安装依赖"""
    print("[INFO] 正在安装依赖...")
    try:
        # 使用 uv pip install 安装依赖
        subprocess.run(['uv', 'pip', 'install', '-r', 'requirements.txt'], check=True)
        print("[SUCCESS] 依赖安装成功")
        return True
    except subprocess.CalledProcessError as e:
        print(f"[ERROR] 安装依赖失败: {e}")
        return False

def install_pyinstaller():
    """安装 PyInstaller"""
    print("[INFO] 正在安装 PyInstaller...")
    try:
        subprocess.run(['uv', 'pip', 'install', 'pyinstaller'], check=True)
        print("[SUCCESS] PyInstaller 安装成功")
        return True
    except subprocess.CalledProcessError as e:
        print(f"[ERROR] 安装 PyInstaller 失败: {e}")
        return False

def build_exe():
    """使用 PyInstaller 打包成 exe"""
    print("[INFO] 开始打包 exe...")
    
    # 确保输出目录存在
    output_dir = Path('aiDAPTIV_Files/Installer')
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # 使用 spec 文件打包
    spec_file = Path('app.spec')
    if spec_file.exists():
        print(f"[INFO] 使用 {spec_file} 进行打包...")
        try:
            subprocess.run(['uv', 'run', 'pyinstaller', 'app.spec', '--clean'], check=True)
            print("[SUCCESS] 打包完成")
            
            # 检查输出文件
            dist_exe = Path('dist/app.exe')
            if dist_exe.exists():
                # 复制到目标目录
                target_exe = output_dir / 'app.exe'
                shutil.copy2(dist_exe, target_exe)
                print(f"[SUCCESS] exe 文件已复制到: {target_exe}")
                return True
            else:
                print("[ERROR] 未找到生成的 exe 文件")
                return False
        except subprocess.CalledProcessError as e:
            print(f"[ERROR] 打包失败: {e}")
            return False
    else:
        print("[ERROR] 未找到 app.spec 文件")
        print("[INFO] 使用基本配置进行打包...")
        try:
            # 基本打包命令
            cmd = [
                'uv', 'run', 'pyinstaller',
                '--onefile',
                '--noconsole',
                '--name=app',
                '--add-data=utils;utils',
                '--add-data=aiDAPTIV_Files;aiDAPTIV_Files',
                '--hidden-import=streamlit',
                '--hidden-import=youtube_transcript_api',
                '--hidden-import=requests',
                '--collect-all=streamlit',
                'app.py'
            ]
            subprocess.run(cmd, check=True)
            print("[SUCCESS] 打包完成")
            
            # 复制到目标目录
            dist_exe = Path('dist/app.exe')
            if dist_exe.exists():
                target_exe = output_dir / 'app.exe'
                shutil.copy2(dist_exe, target_exe)
                print(f"[SUCCESS] exe 文件已复制到: {target_exe}")
                return True
            return False
        except subprocess.CalledProcessError as e:
            print(f"[ERROR] 打包失败: {e}")
            return False

def cleanup():
    """清理临时文件"""
    print("[INFO] 清理临时文件...")
    dirs_to_remove = ['build', '__pycache__']
    for dir_name in dirs_to_remove:
        dir_path = Path(dir_name)
        if dir_path.exists():
            shutil.rmtree(dir_path)
            print(f"[INFO] 已删除: {dir_name}")

def main():
    """主函数"""
    print("=" * 60)
    print("开始构建流程...")
    print("=" * 60)
    
    # 1. 检查 uv
    if not check_uv_installed():
        sys.exit(1)
    
    # 2. 创建虚拟环境
    if not create_venv_with_uv():
        sys.exit(1)
    
    # 3. 安装依赖
    if not install_dependencies():
        sys.exit(1)
    
    # 4. 安装 PyInstaller
    if not install_pyinstaller():
        sys.exit(1)
    
    # 5. 打包 exe
    if not build_exe():
        sys.exit(1)
    
    # 6. 清理
    cleanup()
    
    print("=" * 60)
    print("[SUCCESS] 构建完成！")
    print(f"[INFO] exe 文件位置: aiDAPTIV_Files/Installer/app.exe")
    print("=" * 60)

if __name__ == '__main__':
    main()

