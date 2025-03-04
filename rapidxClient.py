import requests
import json
import time
import hmac
import hashlib
from typing import Dict, Any, Optional

class Client:
    def __init__(self, host: str, config_path: str = ".env"):
        config = self.load_config(config_path)
        self.api_key = config["API_KEY"]
        self.secret_key = config["SECRET_KEY"].encode('utf-8')
        self.host = host
        self.headers = {
            'User-Agent': 'pythonclient/0.0.1',
            'Content-Type': 'application/json',
            'X-MBX-APIKEY': self.api_key
        }
        
    @staticmethod
    def load_config(config_path: str = ".env") -> Dict[str, str]:
        try:
            with open(config_path, 'r') as config_file:
                config = json.load(config_file)
                if not config.get("API_KEY") or not config.get("SECRET_KEY"):
                    raise ValueError("API_KEY or SECRET_KEY is missing in the config file")
                return config
        except FileNotFoundError:
            raise FileNotFoundError(f"Config file not found at {config_path}")
        except json.JSONDecodeError:
            raise ValueError(f"Invalid JSON in config file at {config_path}")


    def get_sign_for_sha256(self, params: Dict[str, Any], nonce: int) -> str:
        payload = self.get_payload(params) + f"&{nonce}"
        return self.hmac_sha256_encrypt_string(payload)

    def hmac_sha256_encrypt_string(self, encrypt_text: str) -> str:
        return hmac.new(
            self.secret_key,
            msg=encrypt_text.encode('utf-8'),
            digestmod=hashlib.sha256
        ).hexdigest()

    @staticmethod
    def get_time_now() -> int:
        return int(time.time())

    @staticmethod
    def get_payload(params: Dict[str, Any]) -> str:
        return '&'.join(f"{key}={value}" for key, value in sorted(params.items()))

    def send_request(self, method: str, endpoint: str, params: Optional[Dict[str, Any]] = None) -> requests.Response:
        url = f"{self.host}{endpoint}"
        params = params or {}
        nonce = self.get_time_now()
        sign = self.get_sign_for_sha256(params, nonce)

        headers = {**self.headers, 'nonce': str(nonce), 'signature': sign}

        try:
            if method == 'GET':
                response = requests.get(url, params=self.get_payload(params), headers=headers)
            elif method == 'POST':
                response = requests.post(url, json=params, headers=headers)
            elif method == 'DELETE':
                response = requests.delete(url, json=params, headers=headers)
            elif method == 'PUT':
                response = requests.put(url, json=params, headers=headers)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")

            return response.json()

        except requests.RequestException as e:
            print(f"Request failed: {e}")
            return e.response if hasattr(e, 'response') else None

    def get_assets(self) -> Optional[requests.Response]:
        return self.send_request('GET', "/api/v1/trading/portfolio/assets")
    
    def get_orders(self) -> Optional[requests.Response]:
        return self.send_request('GET', "/api/v1/trading/orders")
    
    def get_portfolio(self) -> Optional[requests.Response]:
        return self.send_request('GET', "/api/v1/trading/portfolio")
    
    def update_portfolio(self, params) -> Optional[requests.Response]:
        return self.send_request('PUT', "/api/v1/trading/portfolio", params)
    
    def delete_portfolio(self, params) -> Optional[requests.Response]:
        return self.send_request('DELETE', "/api/v1/trading/portfolio", params)
    
    def create_portfolio(self, params) -> Optional[requests.Response]:
        return self.send_request('POST', "/api/v1/trading/portfolio", params)
    
    def create_portfolioAPI(self, params) -> Optional[requests.Response]:
        return self.send_request('POST', "/api/v1/apiKey/portfolio", params)
    
    def update_portfolioAPI(self, params) -> Optional[requests.Response]:
        return self.send_request('PUT', "/api/v1/apiKey/portfolio", params)
    
    def get_portfolioAPI(self) -> Optional[requests.Response]:
        return self.send_request('GET', "/api/v1/apiKey/portfolio")
    
    def delete_portfolioAPI(self, params) -> Optional[requests.Response]:
        return self.send_request('DELETE', "/api/v1/apiKey/portfolio", params)
    
    def cancel_order(self, clientOrderId: str) -> Dict[str, Any]:
        return self.send_request('DELETE', "/api/v1/trading/order", {"clientOrderId": clientOrderId})
    
    def get_positions(self) -> Optional[requests.Response]:
        return self.send_request('GET', "/api/v1/trading/position")
    
    def get_transactions(self, begin=None, end=None, limit=300) -> Optional[requests.Response]:
        params = {}
        if begin is not None:
            params['begin'] = begin
        if end is not None:
            params['end'] = end
        if limit is not None:
            params['limit'] = limit
        
        return self.send_request('GET', "/api/v1/trading/executions", params=params)
    
    def create_portfolio_wrapped(self, name, ip = "13.115.67.82"):
        # Call create_portfolio and store the response
        portfolio_response = self.create_portfolio({"name": name})
        print("Portfolio creation response:", portfolio_response)
        
        # # Check if we got a valid response with portfolioId
        # if not portfolio_response or "portfolioId" not in portfolio_response:
        #     raise Exception("Failed to get portfolioId from create_portfolio response")
        
        # # Proceed with creating portfolio API
        api_response = self.create_portfolioAPI({
            "portfolioId": portfolio_response['data']["portfolioId"],
            "apiName": name,
            "ip": ip,
            "permission": "TRADE"
        })
        print("Portfolio API creation response:", api_response)
        

if __name__ == '__main__':
    client = Client("https://api.liquiditytech.com", ".env")
    result = client.get_orders()
    print(result)