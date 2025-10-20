"""
Simple example of building and posting app data to the endpoints.
"""

from cowdao_cowpy.app_data.utils import PartnerFee, build_all_app_codes


def main():
    app_code = "exampleAppCode"
    referrer_address = "0x1234567890abcdef1234567890abcdef12345678"
    # Example fee structure
    partner_fee_address = "0x1234567890abcdef1234567890abcdef12345679"
    partner_fee = PartnerFee(bps=1, recipient=partner_fee_address)
    env = "prod"
    graffiti = "exampleGraffiti"
    app_data_hash = build_all_app_codes(
        env=env,
        app_code=app_code,
        referrer_address=referrer_address,
        partner_fee=partner_fee,
        graffiti=graffiti,
    )
    print("App data hash:", app_data_hash)


if __name__ == "__main__":
    main()
