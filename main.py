from DCA.ETF import ETF
from DCA.Portfolio import PortfolioETF

def main():
    
    # Create an ETF instance
    etf1 = ETF(name="Amundi MSCI World UCITS ETF", ticker="AMDW", currency="Euro", price=500.0, fees=0.2)
    etf2 = ETF(name="Vanguard S&P 500 UCITS ETF", ticker="VUSA", currency="USD", price=300.0, fees=0.1)
    etf3 = ETF(name="iShares Core MSCI Emerging Markets IMI UCITS ETF", ticker="EIMI", currency="Euro", price=200.0, fees=0.25)
    
    # Create a PortfolioETF instance
    portfolio = PortfolioETF()
    portfolio.add_etf(etf1, portfolio_share=0.5, amount_invested=2000.0)
    portfolio.add_etf(etf2, portfolio_share=0.2, amount_invested=800.0)
    portfolio.add_etf(etf3, portfolio_share=0.3, amount_invested=300.0)
    
    # Compute actual shares based on invested amounts
    actual_shares = portfolio.compute_actual_shares()
    
    # Verify portfolio shares
    portfolio.verify_shares_sum()
    
    # Show for portfolio equilibrium
    #pmatrix = portfolio.generate_shares_matrix(etf1)
    
    # Generate vector of shares
    #invested_vector = portfolio.generate_invested_vector(etf1)
    
    # Solve for equilibrium
    equilibrium = portfolio.solve_equilibrium(etf1)
    
    for elem in equilibrium:
        #print(elem)
        print(f"ETF: {elem['name']}")
        print(f"   Share: {elem['portfolio_share']}, Final Share: {elem['final_share']}")
        print(f"   Amount Invested: {elem['amount_invested']}€, Amount to Invest: {elem['amount_to_invest']}€")



if __name__ == "__main__":
    main()
