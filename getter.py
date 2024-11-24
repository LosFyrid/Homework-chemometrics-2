import pandas as pd
import os
import requests
import time
from pathlib import Path
from bs4 import BeautifulSoup


def read_excel_data(file_path):
    # 读取Excel文件
    df = pd.read_excel(file_path)
    
    # 选择需要的列
    selected_columns = ["DOI", "Article Title", "Times Cited, All Databases"]
    df_selected = df[selected_columns]
    
    # 删除DOI为空的行
    df_selected = df_selected.dropna(subset=['DOI'])
    
    return df_selected

def get_paper_by_doi(doi, email):
    """通过DOI获取论文PDF链接"""
    base_url = f"https://api.unpaywall.org/v2/{doi}?email={email}"
    try:
        print(f"正在获取 DOI: {doi} 的论文链接...")
        response = requests.get(base_url, timeout=10)
        print(f"API响应状态码: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"论文是否开放获取: {data.get('is_oa')}")
            if data.get('is_oa'):
                # 首先检查最佳位置
                best_oa_location = data.get('best_oa_location', {})
                pdf_url = best_oa_location.get('pdf_url') or best_oa_location.get('url_for_pdf')
                
                # 如果最佳位置没有PDF链接，检查所有位置
                if not pdf_url:
                    print("在最佳位置未找到PDF，检查其他位置...")
                    oa_locations = data.get('oa_locations', [])
                    for location in oa_locations:
                        potential_pdf_url = location.get('url_for_pdf') or location.get('pdf_url')
                        if potential_pdf_url:
                            pdf_url = potential_pdf_url
                            print(f"在其他位置找到PDF链接: {pdf_url}")
                            break
                
                if pdf_url:
                    print(f"成功获取PDF链接: {pdf_url}")
                    return pdf_url
                else:
                    print("在所有位置都未找到PDF链接")
            else:
                print("这不是一个开放获取的论文")
        else:
            print(f"API请求失败，状态码: {response.status_code}")
            print(f"响应内容: {response.text}")
        return None
    except Exception as e:
        print(f"获取DOI: {doi} 时发生错误: {str(e)}")
        return None

def download_papers(df, output_folder):
    """下载所有论文到指定文件夹"""
    df = df.copy()
    email = "sunykai.021004@gmail.com"  # 确保使用你的真实邮箱
    
    print(f"开始处理，共有 {len(df)} 篇论文")
    print(f"使用的邮箱: {email}")
    
    output_folder = Path(output_folder)
    output_folder.mkdir(parents=True, exist_ok=True)
    
    df.loc[:, 'PDF_URL'] = None
    df.loc[:, 'PDF_Local_Path'] = None
    
    success_count = 0
    skip_count = 0
    for index, row in df.iterrows():
        print(f"\n===== 处理第 {index+1}/{len(df)} 篇论文 =====")
        doi = row['DOI']
        title = row['Article Title']
        print(f"标题: {title}")
        print(f"DOI: {doi}")
        
        # 先生成文件名，检查是否存在
        safe_title = "".join(c for c in title if c.isalnum() or c in (' ', '-', '_')).strip()
        safe_title = safe_title[:100]
        pdf_path = output_folder / f"{safe_title}.pdf"
        
        # 检查文件是否已存在
        if pdf_path.exists():
            print(f"⚠️ 文件已存在，跳过: {pdf_path}")
            df.at[index, 'PDF_Local_Path'] = str(pdf_path)
            skip_count += 1
            continue
        
        pdf_url = get_paper_by_doi(doi, email)
        df.at[index, 'PDF_URL'] = pdf_url
        
        if pdf_url:
            print(f"正在下载到: {pdf_path}")
            
            if download_pdf(pdf_url, pdf_path):
                df.at[index, 'PDF_Local_Path'] = str(pdf_path)
                print(f"✓ 成功下载: {safe_title}")
                success_count += 1
            else:
                print("下载失败，尝试通过Sci-Hub下载")
                if download_from_scihub(doi, pdf_path):
                    df.at[index, 'PDF_Local_Path'] = str(pdf_path)
                    print(f"✓ 成功通过Sci-Hub下载: {title}")
                else:
                    print(f"✗ 通过Sci-Hub下载失败: {title}")
        else:
            print("未找到PDF链接，尝试通过Sci-Hub下载")
            if download_from_scihub(doi, pdf_path):
                df.at[index, 'PDF_Local_Path'] = str(pdf_path)
                print(f"✓ 成功通过Sci-Hub下载: {title}")
            else:
                print(f"✗ 通过Sci-Hub下载失败: {title}")
        
        print("等待1秒后继续...")
        time.sleep(1)
    
    print(f"\n下载完成！")
    print(f"成功下载: {success_count}/{len(df)} 篇论文")
    print(f"跳过已存在: {skip_count} 篇论文")
    return df

def download_from_scihub(doi, save_path):
    """通过Sci-Hub下载PDF"""
    scihub_url = f"https://sci-hub.se/{doi}"
    try:
        print(f"尝试通过Sci-Hub下载 DOI: {doi}")
        response = requests.get(scihub_url, timeout=30)
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # 查找按钮并提取onclick属性中的链接
            button = soup.find('button', onclick=True)
            if button:
                onclick_content = button['onclick']
                # 提取URL
                start = onclick_content.find("'") + 1
                end = onclick_content.rfind("'")
                pdf_url = onclick_content[start:end]
                
                # 确保PDF链接是完整的URL
                if not pdf_url.startswith('http'):
                    pdf_url = 'https:' + pdf_url
                print(f"从Sci-Hub获取PDF链接: {pdf_url}")
                return download_pdf(pdf_url, save_path)
            else:
                print("未找到PDF下载链接，可能是页面结构变化")
        else:
            print(f"Sci-Hub请求失败，状态码: {response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"网络请求错误: {str(e)}")
    except Exception as e:
        print(f"通过Sci-Hub下载时发生错误: {str(e)}")
    return False

def download_pdf(url, save_path):
    """下载PDF文件"""
    if url:
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
            }
            print(f"正在从 {url} 下载PDF...")
            response = requests.get(url, headers=headers, timeout=30)
            print(f"下载响应状态码: {response.status_code}")
            if response.status_code == 200:
                with open(save_path, 'wb') as f:
                    f.write(response.content)
                return True
            else:
                print(f"下载失败，状态码: {response.status_code}")
        except Exception as e:
            print(f"下载PDF时发生错误: {str(e)}")
    return False




# 测试代码
if __name__ == "__main__":
    print("开始运行程序...")
    try:
        metadata = read_excel_data("metadata.xls")
        print(f"从Excel读取了 {len(metadata)} 条记录")
        
        # 使用所有记录而不是测试数据
        print(f"准备下载所有 {len(metadata)} 篇论文")
        
        output_folder = "downloaded_papers"
        metadata_with_pdfs = download_papers(metadata, output_folder)
        
        print("\n保存结果到Excel...")
        metadata_with_pdfs.to_excel("metadata_with_pdfs.xlsx", index=False)
        print("程序运行结束")
    except Exception as e:
        print(f"程序运行出错: {str(e)}")