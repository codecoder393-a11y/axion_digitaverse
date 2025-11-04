import google.generativeai as genai
import statistics
import os

# --- WARNING: INSECURE API KEY STORAGE ---
# You have chosen to store the API key directly in the code.
# This is NOT RECOMMENDED and is a major security risk.
# If this code is in a public repository, your key will be exposed.
# It is strongly advised to use environment variables instead.

# --- Replace 'YOUR_API_KEY_HERE' with your actual Gemini API key. ---
API_KEY = 'AIzaSyD5W-RWhOj7r61X7sSOGX_BfFzmdqvMn4w'

if API_KEY == 'YOUR_API_KEY_HERE':
    # This will cause a clear error if you forget to replace the placeholder.
    raise ValueError("Please replace 'YOUR_API_KEY_HERE' with your actual Gemini API key in backend/axion_ai.py")

genai.configure(api_key=API_KEY)


class AxionAI:
    def __init__(self, blockchain):
        self.blockchain = blockchain
        # Initialize the generative model
        self.model = genai.GenerativeModel('gemini-1.5-flash')

    def chain_stats(self):
        """Calculates and returns statistics about the blockchain."""
        tx_amounts = [
            b.data.get("amount", 0)
            for b in self.blockchain.chain
            if b.data.get("type") == "transaction"
        ]
        mint_amounts = [
            b.data.get("amount", 0)
            for b in self.blockchain.chain
            if b.data.get("type") == "mint"
        ]
        stats = {
            "total_transactions": len(tx_amounts),
            "total_mints": len(mint_amounts),
            "avg_tx_amount": statistics.mean(tx_amounts) if tx_amounts else 0,
            "avg_mint_amount": statistics.mean(mint_amounts) if mint_amounts else 0,
            "max_tx_amount": max(tx_amounts) if tx_amounts else 0,
            "min_tx_amount": min(tx_amounts) if tx_amounts else 0,
        }
        return stats

    def detect_anomalies(self):
        """Detects anomalous transaction amounts."""
        tx_amounts = [
            b.data.get("amount", 0)
            for b in self.blockchain.chain
            if b.data.get("type") == "transaction"
        ]
        if not tx_amounts:
            return []
        mean = statistics.mean(tx_amounts)
        stdev = statistics.stdev(tx_amounts) if len(tx_amounts) > 1 else 0
        # Identify transactions that are more than 2 standard deviations from the mean
        anomalies = [
            amt for amt in tx_amounts if stdev > 0 and abs(amt - mean) > 2 * stdev
        ]
        return anomalies

    def ask(self, question):
        """Answers a general question using the generative AI model."""
        try:
            context = f"""
            You are Axion AI, a helpful assistant for the Axion Digitaverse blockchain platform.
            The blockchain now supports smart contracts written in Python.
            Here are some current statistics about the blockchain: {self.chain_stats()}
            
            A user is asking a question. Please provide a helpful and concise response.
            
            Question: {question}
            
            Answer:
            """
            response = self.model.generate_content(context)
            return response.text
        except Exception as e:
            # Return a helpful error message to the user if the AI call fails
            return f"Error communicating with the AI model: {e}"


    def code_completion(self, prompt):
        """Completes a Python smart contract code snippet using the AI model."""
        full_prompt = f"""
        You are an expert Python smart contract developer for the Axion Digitaverse blockchain.
        Your task is to complete the following Python smart contract code snippet.
        The contract will be executed in an environment that provides a `self.blockchain` object with methods like `get_balance(address)`.

        Provide only the code completion without any explanations or markdown.
        ---
        {prompt}
        ---
        """
        response = self.model.generate_content(full_prompt)
        return response.text

    def generate_contract(self, contract_type):
        """Generates a complete, secure Python smart contract using the AI model."""
        prompt = f"""
        You are an expert Python smart contract developer for the Axion Digitaverse blockchain.
        Your task is to generate a secure, well-documented, and production-ready Python smart contract.

        The contract MUST be a Python class.
        It MUST have an `__init__` method that can accept arguments.
        It MUST have at least one other method that can be called.
        It will be executed in an environment that provides a `self.blockchain` object with methods like `get_balance(address)` and `transfer(sender, recipient, amount)`.

        Contract Type: '{contract_type}'

        Provide only the Python code for the class, without any explanations or markdown.
        Do not include any import statements.
        """
        response = self.model.generate_content(prompt)
        return response.text

    def data_science_report(self):
        """Generates a data science report with stats, anomalies, and AI-powered optimizations."""
        stats = self.chain_stats()
        anomalies = self.detect_anomalies()
        
        optimization_prompt = f"""
        You are a blockchain performance analyst. Based on the following statistics,
        suggest one or two key optimizations to improve the chain's health.
        The blockchain supports Python smart contracts.
        
        Stats: {stats}
        Anomalies Detected: {anomalies}
        
        Suggestion:
        """
        optimization_response = self.model.generate_content(optimization_prompt)
        
        return {
            "stats": stats,
            "anomalies": anomalies,
            "optimization": optimization_response.text
        }
