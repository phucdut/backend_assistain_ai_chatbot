def email_verify_template(user_name: str, redirect_url: str, mode: int) -> str:
    if mode == 1:
        button_text = "Go to Sign in Page"
        button_style = "background-color: #2c2c2c; color: #ffffff; text-decoration: none; padding: 10px 20px; border-radius: 5px; font-size: 16px;"
        button_link = redirect_url
    elif mode == 2:
        button_text = "Verify Email"
        button_style = "background-color: #2c2c2c; color: #ffffff; text-decoration: none; padding: 10px 20px; border-radius: 5px; font-size: 16px;"
        button_link = redirect_url
    return f"""
            <!DOCTYPE html>
                <html lang="en">

                <head>
                    <meta charset="UTF-8">
                    <meta name="viewport" content="width=device-width, initial-scale=1.0">
                    <title>Verify Email Address for AllyBy AI</title>
                </head>

                <body style="font-family: Arial, sans-serif; margin: 0; padding: 0; background-color: #eff2f4;">
                    <table align="center" border="0" cellpadding="0" cellspacing="0" width="600">
                        <tr>
                            <td align="center">
                                <img src="https://github.com/phucdut/frontend_assistain_ai_chatbot/blob/master/public/logo/allyby%20(2).png?raw=true"
                                    alt="AllyBy AI Logo" style="display: block; width: 200px; margin: 20px auto; border-radius: 10px;">
                            </td>
                        </tr>
                        <tr>
                            <td bgcolor="#ffffff" style="padding: 40px 30px 40px 30px;">
                                <table border="0" cellpadding="0" cellspacing="0" width="100%">
                                    <tr>
                                        <td style="color: #153643; font-size: 28px;">
                                            <b>Hey {user_name},</b>
                                        </td>
                                    </tr>
                                    <tr>
                                        <td style="padding: 20px 0 30px 0; color: #153643; font-size: 16px; line-height: 20px;">
                                            Thanks for registering for an account on AllyBy AI! Before we get started, we just need to
                                            confirm that this is you. Click below to verify your email address:
                                        </td>
                                    </tr>
                                    <tr>
                                        <td style="text-align: center;">
                                            <a href="{button_link}" style="{button_style}">{button_text}</a>
                                        </td>
                                    </tr>
                                </table>
                            </td>
                        </tr>
                        <tr>
                            <td bgcolor="#ffffff" style="padding: 30px 30px 30px 30px;">
                                <hr>
                                <table border="0" cellpadding="0" cellspacing="0" width="100%">
                                    <tr>
                                        <td style="color: #153643; font-size: 14px; text-align: center;">
                                            Term of Service | Privacy Statement
                                        </td>
                                    </tr>
                                </table>
                            </td>
                        </tr>
                    </table>
                </body>

                </html>
            """


def email_forgot_password_template(user_name: str, password_reset: str) -> str:
    return f"""
            <!DOCTYPE html>
                <html lang="en">

                <head>
                    <meta charset="UTF-8">
                    <meta name="viewport" content="width=device-width, initial-scale=1.0">
                    <title>Reset Password for AllyBy AI</title>
                </head>

                <body style="font-family: Arial, sans-serif; margin: 0; padding: 0; background-color: #eff2f4;">
                    <table align="center" border="0" cellpadding="0" cellspacing="0" width="600">
                        <tr>
                            <td align="center">
                                <img src="https://github.com/phucdut/frontend_assistain_ai_chatbot/blob/master/public/logo/allyby%20(2).png?raw=true"
                                    alt="AllyBy AI Logo" style="display: block; width: 200px; margin: 20px auto; border-radius: 10px;">
                            </td>
                        </tr>
                        <tr>
                            <td bgcolor="#ffffff" style="padding: 40px 30px 40px 30px;">
                                <table border="0" cellpadding="0" cellspacing="0" width="100%">
                                    <tr>
                                        <td style="color: #153643; font-size: 28px;">
                                            <b>Hey {user_name},</b>
                                        </td>
                                    </tr>
                                    <tr>
                                        <td style="padding: 20px 0 30px 0; color: #153643; font-size: 16px; line-height: 20px;">
                                            We received a request to reset your password. Please follow the instructions below to reset
                                            your password:
                                        </td>
                                    </tr>
                                    <tr>
                                        <td
                                            style="padding: 20px 0 30px 0; color: #153643; font-size: 20px; line-height: 20px; text-align: center; font-weight: 600; display: flex; justify-content: center; align-items: center;">
                                            <div
                                                style="background-color: #eff2f4; border: 2px solid #2c2c2c; padding: 10px; border-radius: 5px; width: 40%; display: flex; justify-content: center; align-items: center;">
                                                {password_reset}
                                            </div>
                                        </td>
                                    </tr>

                                </table>
                            </td>
                        </tr>
                        <tr>
                            <td bgcolor="#ffffff" style="padding: 30px 30px 30px 30px;">
                                <hr>
                                <table border="0" cellpadding="0" cellspacing="0" width="100%">
                                    <tr>
                                        <td style="color: #153643; font-size: 14px; text-align: center;">
                                            Term of Service | Privacy Statement
                                        </td>
                                    </tr>
                                </table>
                            </td>
                        </tr>
                    </table>
                </body>

                </html>
            """


def email_receipt_template(display_name, plan_title, order_number, order_date, payment_method, plan_price):
    return f"""
    <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta http-equiv="X-UA-Compatible" content="IE=edge">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Your Receipt</title>
        </head>
        <body style="font-family: Arial, sans-serif; margin: 0; padding: 0; background-color: #f4f4f4;">
            <table cellpadding="0" cellspacing="0" border="0" width="100%" style="max-width: 600px; margin: 20px auto; padding: 20px; background-color: #fff; border-radius: 5px; box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);">
                <tr>
                    <td>
                        <img src="https://i.imgur.com/9timw95.png" alt="Company Logo" style="display: block; width: 200px; margin-bottom: 20px;">
                        <h2 style="color: #333;">Your Receipt for Monthly Premium Subscription</h2>
                        <p>Dear {display_name},</p>
                        <p>Thank you for choosing AllyBy AI! We're delighted to confirm your recent subscription of {plan_title}.</p>
                        <p>Below, you'll find the details of your transaction:</p>
                        <table cellpadding="0" cellspacing="0" border="0" width="100%">
                            <tr>
                                <td><strong>Order Number:</strong></td>
                                <td>{order_number}</td>
                            </tr>
                            <tr>
                                <td><strong>Date of Purchase:</strong></td>
                                <td>{order_date}</td>
                            </tr>
                            <tr>
                                <td><strong>Payment Method:</strong></td>
                                <td>{payment_method}</td>
                            </tr>
                            <tr>
                                <td><strong>Total Amount:</strong></td>
                                <td>{plan_price}</td>
                            </tr>
                        </table>
                        <p><strong>Items Purchased:</strong></p>
                        <table cellpadding="0" cellspacing="0" border="0" width="100%">
                            <tr>
                                <td>{plan_title}</td>
                                <td>{plan_price}</td>
                            </tr>
                            <!-- Add more items as necessary -->
                        </table>
                        <p><strong>Total Amount Paid:</strong> {plan_price}</p>
                        <p>Your purchase is important to us, and we're committed to ensuring your satisfaction. If you have any questions or concerns regarding your order, please don't hesitate to reach out to our customer support team at support@AllyBy.com.</p>
                        <p>Thank you again for your business!</p>
                        <p style="margin-top: 20px; font-size: 12px; color: #777; text-align: center;">Warm regards,<br>AllyBy AI<br>05 Ngo Si Lien, Danang, Vietnam</p>
                    </td>
                </tr>
            </table>
        </body>
        </html>

    """