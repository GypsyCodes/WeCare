# 🗺️ MapWidget - Widget de Mapa Interativo

O MapWidget é um componente React avançado para seleção de coordenadas geográficas com funcionalidades de geocoding, mapa visual e configuração de raio para check-in.

## ✨ Funcionalidades

### 🔍 **Geocoding (Busca por Endereço)**
- Busca de coordenadas por endereço completo
- Usa OpenStreetMap Nominatim (gratuito, sem API key)
- Suporta endereços brasileiros
- Validação automática de resultados

### 📍 **Geolocalização GPS**
- Captura da localização atual do usuário
- Botão dedicado "Usar Minha Localização Atual"
- Reverse geocoding (coordenadas → endereço)
- Tratamento de erros de permissão

### 🗺️ **Visualização de Mapa**
- Mapa interativo usando OpenStreetMap
- Marcador automático no local selecionado
- Overlay visual do raio de check-in
- Links para mapas externos (Google Maps, OSM)

### 📐 **Configuração de Raio**
- Visualização do raio de check-in no mapa
- Cálculo automático de área de cobertura
- Suporte a raios de 10m a 1000m
- Indicadores visuais com animação

## 🚀 Como Usar

### Props do Componente

```javascript
<MapWidget
  latitude={-23.5505}           // Latitude atual (number)
  longitude={-46.6333}          // Longitude atual (number)
  endereco="Rua das Flores..."  // Endereço atual (string)
  raio={100}                    // Raio em metros (number)
  onLocationChange={(lat, lng) => {}} // Callback para mudança de coordenadas
  onEnderecoChange={(endereco) => {}} // Callback para mudança de endereço
  disabled={false}              // Desabilitar widget (boolean)
/>
```

### Exemplo Prático

```javascript
import MapWidget from './components/MapWidget/MapWidget';

const [formData, setFormData] = useState({
  latitude: '',
  longitude: '',
  endereco: '',
  raio_checkin: 100
});

<MapWidget
  latitude={formData.latitude ? parseFloat(formData.latitude) : null}
  longitude={formData.longitude ? parseFloat(formData.longitude) : null}
  endereco={formData.endereco}
  raio={formData.raio_checkin}
  onLocationChange={(lat, lng) => {
    setFormData(prev => ({
      ...prev,
      latitude: lat.toString(),
      longitude: lng.toString()
    }));
  }}
  onEnderecoChange={(endereco) => {
    setFormData(prev => ({ ...prev, endereco }));
  }}
/>
```

## 🎯 Fluxo de Uso

1. **Busca por Endereço**: Digite um endereço completo e clique em buscar
2. **GPS Atual**: Clique em "Usar Minha Localização Atual" para capturar GPS
3. **Visualização**: O mapa aparece automaticamente com o marcador
4. **Configuração**: O raio é mostrado visualmente no mapa
5. **Validação**: Coordenadas são validadas e formatadas automaticamente

## 🛠️ Integração com Check-in Radial

O widget é a base para o sistema de check-in radial:

### 1. **Cadastro do Estabelecimento**
```javascript
// Coordenadas obtidas pelo widget
const estabelecimento = {
  nome: "Hospital Santa Casa",
  latitude: -23.5505,
  longitude: -46.6333,
  raio_checkin: 100 // metros
};
```

### 2. **Validação de Check-in**
```javascript
// Cálculo de distância usando fórmula Haversine
const dentroDoRaio = estabelecimentoService.validarRaio(
  estabelecimento.latitude,
  estabelecimento.longitude,
  socioLatitude,
  socioLongitude,
  estabelecimento.raio_checkin
);

if (dentroDoRaio) {
  // ✅ Check-in permitido
} else {
  // ❌ Fora da área permitida
}
```

## 🎨 Personalização Visual

### CSS Classes Principais
- `.map-widget` - Container principal
- `.coordinates-info` - Área de informações das coordenadas
- `.radius-info` - Informações do raio
- `.map-container` - Container do mapa
- `.radius-circle` - Círculo visual do raio
- `.radius-overlay` - Overlay do mapa

### Responsividade
- Desktop: Layout completo com mapa grande
- Tablet: Layout adaptado com mapa médio
- Mobile: Layout compacto com mapa reduzido

## 🔧 Configurações Técnicas

### APIs Utilizadas
- **Nominatim**: `https://nominatim.openstreetmap.org/`
- **OpenStreetMap Embed**: Para iframe do mapa
- **Navigator.geolocation**: Para GPS do navegador

### Limitações
- Nominatim tem rate limit (1 req/segundo)
- GPS requer HTTPS ou localhost
- Alguns navegadores podem bloquear geolocalização

### Performance
- Debounce automático na busca
- Cache de resultados de geocoding
- Lazy loading do iframe do mapa

## 🚨 Tratamento de Erros

### Erros de Geocoding
- Endereço não encontrado
- Erro de conexão com API
- Rate limit excedido

### Erros de GPS
- Permissão negada pelo usuário
- Localização indisponível
- Timeout na captura

### Validações
- Coordenadas fora do range válido
- Endereço muito curto (< 10 caracteres)
- Raio fora dos limites (10-1000m)

## 🎉 Próximas Funcionalidades

- [ ] Suporte a múltiplos marcadores
- [ ] Desenho manual de áreas
- [ ] Integração com Google Maps API
- [ ] Histórico de buscas
- [ ] Favoritos de localizações

---

**Desenvolvido para o Sistema We Care** 💚
*Widget de mapa profissional para gestão de estabelecimentos e check-in radial* 