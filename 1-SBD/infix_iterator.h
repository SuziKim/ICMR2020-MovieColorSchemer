#if !defined INFIX_ITERATOR_H
#define INFIX_ITERATOR_H

#include <ostream> 
#include <iterator> 

	// TEMPLATE CLASS infix_ostream_iterator

template<class _Ty,
	class _Elem = char,
	class _Traits = std::char_traits<_Elem> >
	class infix_ostream_iterator
		: public std::_Outit
	{	// wrap _Ty inserts to output stream as output iterator
public:
	typedef _Elem char_type;
	typedef _Traits traits_type;
	typedef std::basic_ostream<_Elem, _Traits> ostream_type;

	infix_ostream_iterator(ostream_type& _Ostr,
		const _Elem *_Delim = 0)
		: _Myostr(&_Ostr), _Mydelim(_Delim), _Myfirst_elem(true)
	{	// construct from output stream and delimiter
	}

	infix_ostream_iterator<_Ty, _Elem, _Traits>& operator=(const _Ty& _Val)
	{	// insert delimiter into output stream, followed by value
		if (!_Myfirst_elem && _Mydelim != 0)
			*_Myostr << _Mydelim;
		*_Myostr << _Val;
		_Myfirst_elem = false;
		return (*this);
	}

	infix_ostream_iterator<_Ty, _Elem, _Traits>& operator*()
	{	// pretend to return designated value
		return (*this);
	}

	infix_ostream_iterator<_Ty, _Elem, _Traits>& operator++()
	{	// pretend to preincrement
		return (*this);
	}

	infix_ostream_iterator<_Ty, _Elem, _Traits>& operator++(int)
	{	// pretend to postincrement
		return (*this);
	}

protected:
	const _Elem *_Mydelim;	// pointer to delimiter string (NB: not freed)
	ostream_type *_Myostr;	// pointer to output stream
	bool _Myfirst_elem;
};


template<class _Ty,
	class _Elem,
	class _Traits>
	struct std::_Is_checked_helper<infix_ostream_iterator<_Ty, _Elem, _Traits> >
		: public std::true_type
	{	// mark ostream_iterator as checked
	};

#endif 
