from .models import LoyaltyPoints, PointsHistory

def award_points(user, order_amount, order_id=None):
    points_earned = int(order_amount // 100)  # 1 point per ₹100 spent

    if points_earned <= 0:
        return

    loyalty, created = LoyaltyPoints.objects.get_or_create(user=user)
    loyalty.balance += points_earned
    loyalty.save()

    PointsHistory.objects.create(
        user=user,
        points=points_earned,
        type=PointsHistory.EARNED,
        description=f"Earned from Order #{order_id}" if order_id else "Earned from purchase"
    )


def redeem_points(user, points_to_redeem):
    loyalty, created = LoyaltyPoints.objects.get_or_create(user=user)

    if points_to_redeem > loyalty.balance:
        return False, "Insufficient points balance"

    loyalty.balance -= points_to_redeem
    loyalty.save()

    PointsHistory.objects.create(
        user=user,
        points=-points_to_redeem,
        type=PointsHistory.REDEEMED,
        description="Redeemed at checkout"
    )

    return True, "Points redeemed successfully"