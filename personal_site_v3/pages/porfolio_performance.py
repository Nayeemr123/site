if not data.empty:
    st.write("#### Price Comparison")
    
    col1, col2 = st.columns(2, gap='Large')
    with col1:
        st.write("Comparison Chart")
        fig = px.line(data, x=data.index, y=data.columns)
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.write("Adj Close Prices Ordered by Date")
        st.write(data)

    st.write("#### ROI")
    st.write(f"{start_date.strftime('%Y/%m/%d')} to {end_date.strftime('%Y/%m/%d')}")
    st.write("Discover how your investments grow over time! Enter your initial investment amount and select a time period to calculate your potential return on investment (ROI). Visualize the performance of your investments with interactive charts, tracking daily, weekly, and monthly growth or decline. This tool helps you make informed financial decisions whether you're planning for the future or analyzing past performance,")

    col3, col4 = st.columns(2, gap='Large')
    with col3:
        # Calculate ROI based on the initial investment amount
        investment_amount = st.number_input("Enter investment amount ($)", min_value=0, value=1000)

    with col4:
        roi_data = []
        growth_data = pd.DataFrame(index=data.index)
        for ticker in data.columns:
            initial_price = data[ticker].iloc[0]
            latest_price = data[ticker].iloc[-1]
            shares_purchased = investment_amount / initial_price
            final_value = round(shares_purchased * latest_price, 2)
            roi = round(final_value - investment_amount, 2)
            roi_percentage = round(((latest_price - initial_price) / initial_price) * 100, 2)  # Same as growth rate

            roi_data.append({
                "Ticker": ticker,
                "Initial Price": initial_price,
                "Latest Price": latest_price,
                "Shares Purchased": shares_purchased,
                "Final Value": final_value,
                "ROI ($)": roi,
                "ROI (%)": roi_percentage
            })

            # Calculate growth or decline for each date
            growth_data[ticker] = (data[ticker] / initial_price - 1) * investment_amount

        roi_df = pd.DataFrame(roi_data)
        st.write("ROI Data Table")
        st.write(roi_df)

    # Plot the growth or decline of the investment amount
    st.write("#### Growth or Decline of Investment Amount")
    fig_growth = px.line(growth_data, x=growth_data.index, y=growth_data.columns, labels={'value': 'Growth/Decline ($)'})
    st.plotly_chart(fig_growth, use_container_width=True)

    # Add a dropdown menu for selecting the view for growth rate comparison
    view_option = st.selectbox(
        "Select view for growth rate chart",
        options=["Daily", "Monthly", "Yearly"],
        index=1  # Default to Monthly
    )
