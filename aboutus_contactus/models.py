from django.core.cache import cache
from django.db import models
from django.contrib.auth import get_user_model

user_model = get_user_model()


class ContactUs(models.Model):
    tickets = [
        ('orders', 'سفارشات'), ('payment', 'امور مالی'), ('jobbing', 'همکاری'), ('guid', 'راهنمایی'), ('others', 'سایر')
    ]
    user = models.ForeignKey(user_model, on_delete=models.CASCADE, verbose_name='کاربر', related_name='contacts')
    ticket = models.CharField(max_length=100, choices=tickets, verbose_name='تیکت')
    text = models.TextField(verbose_name='متن پیام')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='تاریخ ایجاد')
    answered = models.BooleanField(default=False, verbose_name='پاسخ داده شده ')

    class Meta:
        verbose_name = 'تیکت کاربر'
        verbose_name_plural = ' تیکت های کاربران'
        ordering = ['created_at', 'answered']

    def __str__(self):
        return f'{self.ticket} - {self.text:40}'


class ReplyContact(models.Model):
    reply_to = models.ForeignKey(ContactUs, on_delete=models.CASCADE, verbose_name='پاسخ به پیام',
                                 related_name='reply_contact', null=True, blank=True)
    user = models.ForeignKey(user_model, on_delete=models.CASCADE, verbose_name='کاربر', related_name='reply_contacts',
                             null=True, blank=True)
    text = models.TextField(verbose_name='متن پیام')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='تاریخ پاسخ')
    is_read = models.BooleanField(default=False, verbose_name='خوانده شده ')

    class Meta:
        verbose_name = 'پاسخ به کاربر'
        verbose_name_plural = 'پاسخ به کاربران'
        ordering = ['created_at']

    def save(self, *args, **kwargs):
        cache_key = f'{self.user.id}_messages_count'
        cache.delete(cache_key)
        if not self.pk and self.reply_to:
            self.user = self.reply_to.user
        super().save(*args, **kwargs)
        if self.reply_to and not self.reply_to.answered:
            self.reply_to.answered = True
            self.reply_to.save(update_fields=['answered'])

    def __str__(self):
        return f'{self.reply_to} - {self.text:40}'
