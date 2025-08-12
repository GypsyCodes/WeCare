#!/usr/bin/env python3
"""
Script para testar endpoints da API We Care
Execute enquanto o servidor está rodando
"""
import requests
import json
import time

def test_endpoint(url, name):
    """Teste um endpoint específico"""
    try:
        print(f"🧪 Testando {name}...")
        response = requests.get(url, timeout=5)
        
        if response.status_code == 200:
            # Swagger/docs retorna HTML, não JSON
            if '/docs' in url:
                print(f"✅ {name}: {response.status_code}")
                print(f"📝 Resposta: Página Swagger carregada (HTML)")
                return True
            else:
                data = response.json()
                print(f"✅ {name}: {response.status_code}")
                print(f"📝 Resposta: {json.dumps(data, ensure_ascii=False, indent=2)}")
                return True
        else:
            print(f"❌ {name}: {response.status_code}")
            print(f"📝 Erro: {response.text}")
            return False
            
    except requests.exceptions.ConnectionError:
        print(f"🔌 {name}: Servidor não está rodando")
        return False
    except requests.exceptions.Timeout:
        print(f"⏰ {name}: Timeout")
        return False
    except Exception as e:
        print(f"❌ {name}: Erro - {e}")
        return False

def main():
    """Função principal"""
    print("🚀 Teste dos Endpoints - We Care API")
    print("="*50)
    
    base_url = "http://127.0.0.1:8000"
    
    # Lista de endpoints para testar
    endpoints = [
        ("/", "Health Check"),
        ("/test-db", "Teste Banco de Dados"),
        ("/test-tables", "Lista Tabelas"),
        ("/docs", "Documentação Swagger"),
    ]
    
    results = []
    
    for endpoint, name in endpoints:
        url = f"{base_url}{endpoint}"
        success = test_endpoint(url, name)
        results.append((name, success))
        print("-" * 50)
        time.sleep(1)  # Delay entre testes
    
    # Resumo
    print("\n📊 RESUMO DOS TESTES:")
    print("="*50)
    
    passed = sum(1 for _, success in results if success)
    total = len(results)
    
    for name, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} - {name}")
    
    print(f"\n🎯 Resultado: {passed}/{total} testes passaram")
    
    if passed == total:
        print("🎉 TODOS OS TESTES PASSARAM!")
        print("\n📋 Próximos passos:")
        print("1. ✅ Banco de dados funcionando")
        print("2. ✅ API respondendo")
        print("3. 🔄 Criar usuário administrador")
        print("4. 🚀 Deploy para produção")
    else:
        print(f"⚠️  {total - passed} teste(s) falharam")
        print("Verifique se o servidor está rodando e o MySQL está ativo")

if __name__ == "__main__":
    main()
    input("\nPressione Enter para continuar...") 